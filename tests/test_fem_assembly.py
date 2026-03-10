import json

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from src.fem import Assemblatore, CaricoDistribuitoUniforme, ElementoBeam, ModelloFEM, Nodo


def test_modello_fem_costruisce_mappa_gdl_con_id_arbitrari() -> None:
    nodi = [Nodo(id=10, x=0.0, y=0.0), Nodo(id=30, x=500.0, y=0.0)]
    elementi = [
        ElementoBeam(E=30000.0, A=25.0, I=1000.0, L=500.0, id_nodo_iniziale=10, id_nodo_finale=30)
    ]

    modello = ModelloFEM(nodi=nodi, elementi=elementi)

    assert modello.n_gdl == 6
    assert modello.dof_nodo(10) == (0, 1, 2)
    assert modello.dof_nodo(30) == (3, 4, 5)
    assert modello.dof_elemento(elementi[0]) == (0, 1, 2, 3, 4, 5)


def test_modello_fem_rifiuta_geometria_elemento_incoerente() -> None:
    nodi = [Nodo(id=1, x=0.0, y=0.0), Nodo(id=2, x=500.0, y=0.0)]
    elementi = [
        ElementoBeam(E=30000.0, A=25.0, I=1000.0, L=400.0, id_nodo_iniziale=1, id_nodo_finale=2)
    ]

    with pytest.raises(ValueError, match="distanza nodale"):
        ModelloFEM(nodi=nodi, elementi=elementi)


def test_assemblatore_produce_matrice_csr_simmetrica_per_portale_semplice() -> None:
    nodi = [
        Nodo(id=1, x=0.0, y=0.0),
        Nodo(id=2, x=0.0, y=300.0),
        Nodo(id=3, x=400.0, y=300.0),
        Nodo(id=4, x=400.0, y=0.0),
    ]
    elementi = [
        ElementoBeam(
            E=2100000.0,
            A=40.0,
            I=6000.0,
            L=300.0,
            angolo=np.pi / 2.0,
            id_nodo_iniziale=1,
            id_nodo_finale=2,
        ),
        ElementoBeam(
            E=2100000.0,
            A=30.0,
            I=4500.0,
            L=400.0,
            id_nodo_iniziale=2,
            id_nodo_finale=3,
            etichetta="trave",
        ),
        ElementoBeam(
            E=2100000.0,
            A=40.0,
            I=6000.0,
            L=300.0,
            angolo=-np.pi / 2.0,
            id_nodo_iniziale=3,
            id_nodo_finale=4,
        ),
    ]
    modello = ModelloFEM(
        nodi=nodi,
        elementi=elementi,
        carichi_nodali={3: np.array([0.0, -1200.0, 0.0])},
    )

    matrice, vettore = Assemblatore(modello).assembla()

    assert isinstance(matrice, csr_matrix)
    assert matrice.shape == (12, 12)
    assert matrice.nnz > 0
    np.testing.assert_allclose((matrice - matrice.T).toarray(), np.zeros((12, 12)), atol=1e-9)
    np.testing.assert_allclose(vettore[6:9], np.array([0.0, -1200.0, 0.0]), atol=1e-12)


def test_assemblatore_somma_carichi_nodali_e_equivalenti_di_elemento() -> None:
    nodi = [Nodo(id=1, x=0.0, y=0.0), Nodo(id=2, x=500.0, y=0.0)]
    elemento = ElementoBeam(
        E=30000.0,
        A=25.0,
        I=1000.0,
        L=500.0,
        id_nodo_iniziale=1,
        id_nodo_finale=2,
        etichetta="architrave",
    )
    modello = ModelloFEM(
        nodi=nodi,
        elementi=[elemento],
        carichi_nodali={2: np.array([10.0, -20.0, 30.0])},
        carichi_elementi={"architrave": [CaricoDistribuitoUniforme(intensita=-2.0)]},
    )

    _, vettore = Assemblatore(modello).assembla()

    expected = np.array([0.0, -500.0, -41666.666666666664, 10.0, -520.0, 41696.666666666664])
    np.testing.assert_allclose(vettore, expected, rtol=1e-12, atol=1e-12)


def test_modello_fem_from_dict_supporta_carichi_serializzati() -> None:
    data = {
        "etichetta": "portale_test",
        "metadati": {"autore": "test"},
        "vincoli": [{"id_nodo": 1, "tipo": "incastro"}],
        "nodi": [
            {"id": 5, "x": 0.0, "y": 0.0},
            {"id": 9, "x": 500.0, "y": 0.0},
        ],
        "elementi": [
            {
                "E": 30000.0,
                "A": 25.0,
                "I": 1000.0,
                "id_nodo_iniziale": 5,
                "id_nodo_finale": 9,
                "etichetta": "trave_1",
            }
        ],
        "carichi_nodali": {"9": [0.0, -1000.0, 0.0]},
        "carichi_elementi": {
            "trave_1": [{"tipo": "carico_distribuito_uniforme", "intensita": -2.0}]
        },
    }

    modello = ModelloFEM.from_dict(data)

    assert modello.etichetta == "portale_test"
    assert modello.metadati == {"autore": "test"}
    assert modello.vincoli == [{"id_nodo": 1, "tipo": "incastro"}]
    assert modello.elementi[0].L == pytest.approx(500.0)
    assert modello.elementi[0].angolo_rad == pytest.approx(0.0)
    assert isinstance(
        modello.carichi_per_elemento(0, modello.elementi[0])[0], CaricoDistribuitoUniforme
    )


def test_modello_fem_roundtrip_json_preserva_schema_esteso(
    tmp_path: pytest.TempPathFactory,
) -> None:
    modello = ModelloFEM(
        nodi=[Nodo(id=1, x=0.0, y=0.0), Nodo(id=2, x=500.0, y=0.0)],
        elementi=[
            ElementoBeam(
                E=30000.0,
                A=25.0,
                I=1000.0,
                L=500.0,
                id_nodo_iniziale=1,
                id_nodo_finale=2,
                etichetta="E1",
            )
        ],
        carichi_nodali={2: np.array([0.0, -1000.0, 0.0])},
        carichi_elementi={"E1": [CaricoDistribuitoUniforme(intensita=-2.0)]},
        etichetta="modello_json",
        metadati={"versione": "m2"},
        vincoli=[{"id_nodo": 1, "tipo": "incastro"}],
    )

    path = tmp_path / "modello.json"
    path.write_text(json.dumps(modello.to_dict(), ensure_ascii=False), encoding="utf-8")

    ricaricato = ModelloFEM.from_json(path)

    assert ricaricato.etichetta == "modello_json"
    assert ricaricato.metadati == {"versione": "m2"}
    assert ricaricato.vincoli == [{"id_nodo": 1, "tipo": "incastro"}]
    np.testing.assert_allclose(ricaricato.carichi_nodali[2], np.array([0.0, -1000.0, 0.0]))
    assert ricaricato.elementi[0].etichetta == "E1"


def test_modello_fem_from_csv_legge_nodi_ed_elementi(tmp_path: pytest.TempPathFactory) -> None:
    path_nodi = tmp_path / "nodi_m2.csv"
    path_elementi = tmp_path / "elementi_m2.csv"

    path_nodi.write_text("id,x,y\n10,0.0,0.0\n30,500.0,0.0\n", encoding="utf-8")
    path_elementi.write_text(
        "E,A,I,id_nodo_iniziale,id_nodo_finale,etichetta\n30000.0,25.0,1000.0,10,30,TR1\n",
        encoding="utf-8",
    )

    modello = ModelloFEM.from_csv(path_nodi, path_elementi)

    assert modello.dof_nodo(10) == (0, 1, 2)
    assert modello.dof_nodo(30) == (3, 4, 5)
    assert modello.elementi[0].L == pytest.approx(500.0)
    assert modello.elementi[0].etichetta == "TR1"


def test_verifica_connettivita_segnala_nodi_isolati() -> None:
    modello = ModelloFEM(
        nodi=[Nodo(id=1, x=0.0, y=0.0), Nodo(id=2, x=500.0, y=0.0), Nodo(id=9, x=900.0, y=0.0)],
        elementi=[
            ElementoBeam(E=30000.0, A=25.0, I=1000.0, L=500.0, id_nodo_iniziale=1, id_nodo_finale=2)
        ],
    )

    warning = Assemblatore(modello).verifica_connettivita()

    assert any("Nodi isolati" in voce for voce in warning)
