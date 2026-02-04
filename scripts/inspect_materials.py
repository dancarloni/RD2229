from tools import materials_manager


def main():
    mats = materials_manager.list_materials()
    for m in mats:
        if m.get("name") in ("CA-01", "CA-02", "CA-03"):
            print(m.get("name"))
            print("E_calculated:", m.get("E_calculated"))
            print("E_conventional:", m.get("E_conventional"))
            print("G_min,G_max:", m.get("G_min"), m.get("G_max"))
            print("E:", m.get("E"), "E_defined:", m.get("E_defined"))
            print("---")


if __name__ == "__main__":
    main()

