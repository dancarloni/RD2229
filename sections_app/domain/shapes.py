"""Implementazioni concrete delle varie forme di sezione."""

import math

from ..services.calculations import rotate_inertia
from .base import Section, SectionProperties


class RectangularSection(Section):
    """Sezione rettangolare."""

    @property
    def section_type(self) -> str:
        return "RECTANGULAR"

    def _compute_geometric_properties(self) -> SectionProperties:
        """Calcola le proprietà geometriche della sezione rettangolare."""
        width = self.dimensions.get("width", 0)
        height = self.dimensions.get("height", 0)

        if width <= 0 or height <= 0:
            raise ValueError("Dimensioni non valide per la sezione rettangolare")

        # Area: può essere fornita direttamente o calcolata
        area_override = self.dimensions.get("area")
        if area_override is not None:
            if area_override > 0:
                area = area_override
            else:
                import warnings
                warnings.warn(
                    f"Area override non valida ({area_override}), uso calcolo automatico",
                    UserWarning,
                    stacklevel=2
                )
                area = width * height
        else:
            area = width * height

        # Centro di gravità
        x_g = width / 2
        y_g = height / 2

        # Momenti di inerzia locali (assi non ruotati)
        ix_local = (width * height**3) / 12
        iy_local = (height * width**3) / 12
        ixy_local = 0.0

        # Applica rotazione se necessario
        if self.rotation_angle_deg != 0:
            angle_rad = math.radians(self.rotation_angle_deg)
            Ix, Iy, Ixy = rotate_inertia(ix_local, iy_local, ixy_local, angle_rad)
        else:
            Ix, Iy, Ixy = ix_local, iy_local, ixy_local

        # Proprietà shear
        kappa_y, kappa_z = self.get_default_shear_kappas()

        # Aree shear
        from ..services import compute_shear_areas
        A_y, A_z = compute_shear_areas(self)

        # Proprietà shear Qx, Qy
        Qx = area * y_g
        Qy = area * x_g

        return SectionProperties(
            area=area,
            A_y=A_y,
            A_z=A_z,
            kappa_y=kappa_y,
            kappa_z=kappa_z,
            x_g=x_g,
            y_g=y_g,
            Ix=Ix,
            Iy=Iy,
            Ixy=Ixy,
            Qx=Qx,
            Qy=Qy,
        )


class CircularSection(Section):
    """Sezione circolare piena."""

    @property
    def section_type(self) -> str:
        return "CIRCULAR"

    def _compute_geometric_properties(self) -> SectionProperties:
        """Calcola le proprietà geometriche della sezione circolare."""
        diameter = self.dimensions.get("diameter", 0)

        if diameter <= 0:
            raise ValueError("Diametro non valido per la sezione circolare")

        radius = diameter / 2

        # Area: può essere fornita direttamente o calcolata
        area_override = self.dimensions.get("area")
        if area_override is not None:
            if area_override > 0:
                area = area_override
            else:
                import warnings
                warnings.warn(
                    f"Area override non valida ({area_override}), uso calcolo automatico",
                    UserWarning,
                    stacklevel=2
                )
                area = math.pi * radius**2
        else:
            area = math.pi * radius**2

        # Centro di gravità
        x_g = radius
        y_g = radius

        # Momenti di inerzia locali (circolare è simmetrica)
        ix_local = (math.pi * radius**4) / 4
        iy_local = ix_local
        ixy_local = 0.0

        # Applica rotazione (per circolare non cambia, ma manteniamo coerenza)
        if self.rotation_angle_deg != 0:
            angle_rad = math.radians(self.rotation_angle_deg)
            Ix, Iy, Ixy = rotate_inertia(ix_local, iy_local, ixy_local, angle_rad)
        else:
            Ix, Iy, Ixy = ix_local, iy_local, ixy_local

        # Proprietà shear
        kappa_y, kappa_z = self.get_default_shear_kappas()

        # Aree shear
        from ..services import compute_shear_areas
        A_y, A_z = compute_shear_areas(self)

        # Proprietà shear Qx, Qy
        Qx = area * y_g
        Qy = area * x_g

        # Core section
        core_x = radius / 4
        core_y = radius / 4

        return SectionProperties(
            area=area,
            A_y=A_y,
            A_z=A_z,
            kappa_y=kappa_y,
            kappa_z=kappa_z,
            x_g=x_g,
            y_g=y_g,
            Ix=Ix,
            Iy=Iy,
            Ixy=Ixy,
            Qx=Qx,
            Qy=Qy,
            core_x=core_x,
            core_y=core_y,
        )


class TSection(Section):
    """Sezione a T."""

    @property
    def section_type(self) -> str:
        return "T_SECTION"

    def _compute_geometric_properties(self) -> SectionProperties:
        """Calcola le proprietà geometriche della sezione a T."""
        flange_width = self.dimensions.get("flange_width", 0)
        flange_thickness = self.dimensions.get("flange_thickness", 0)
        web_thickness = self.dimensions.get("web_thickness", 0)
        web_height = self.dimensions.get("web_height", 0)

        if any(x <= 0 for x in [flange_width, flange_thickness, web_thickness, web_height]):
            raise ValueError("Dimensioni non valide per la sezione a T")

        # Area componenti
        area_flange = flange_width * flange_thickness
        area_web = web_thickness * web_height
        calculated_area = area_flange + area_web

        # Area: può essere fornita direttamente o calcolata
        area_override = self.dimensions.get("area")
        if area_override is not None:
            if area_override > 0:
                area = area_override
            else:
                import warnings
                warnings.warn(
                    f"Area override non valida ({area_override}), uso calcolo automatico",
                    UserWarning,
                    stacklevel=2
                )
                area = calculated_area
        else:
            area = calculated_area

        # Centro di gravità (rispetto al fondo dell'anima)
        y_flange = web_height + flange_thickness / 2
        x_g = flange_width / 2
        y_g = (area_flange * y_flange + area_web * (web_height / 2)) / calculated_area

        # Momenti di inerzia locali rispetto al centro di gravità
        # Flangia
        ix_flange = (flange_width * flange_thickness**3) / 12 + area_flange * (
            y_flange - y_g
        ) ** 2
        iy_flange = (flange_thickness * flange_width**3) / 12

        # Anima
        ix_web = (web_thickness * web_height**3) / 12 + area_web * (
            web_height / 2 - y_g
        ) ** 2
        iy_web = (web_height * web_thickness**3) / 12

        ix_local = ix_flange + ix_web
        iy_local = iy_flange + iy_web
        ixy_local = 0.0

        # Applica rotazione se necessario
        if self.rotation_angle_deg != 0:
            angle_rad = math.radians(self.rotation_angle_deg)
            Ix, Iy, Ixy = rotate_inertia(ix_local, iy_local, ixy_local, angle_rad)
        else:
            Ix, Iy, Ixy = ix_local, iy_local, ixy_local

        # Proprietà shear
        kappa_y, kappa_z = self.get_default_shear_kappas()

        # Aree shear
        from ..services import compute_shear_areas
        A_y, A_z = compute_shear_areas(self)

        # Proprietà shear Qx, Qy (semplificate)
        Qx = area * y_g
        Qy = area * x_g

        # Core section (semplificato)
        core_x = Iy / (area * (flange_width / 2))
        core_y = Ix / (area * (web_height / 2))

        return SectionProperties(
            area=area,
            A_y=A_y,
            A_z=A_z,
            kappa_y=kappa_y,
            kappa_z=kappa_z,
            x_g=x_g,
            y_g=y_g,
            Ix=Ix,
            Iy=Iy,
            Ixy=Ixy,
            Qx=Qx,
            Qy=Qy,
            core_x=core_x,
            core_y=core_y,
        )


class LSection(Section):
    """Sezione ad L."""

    @property
    def section_type(self) -> str:
        return "L_SECTION"

    def _compute_geometric_properties(self):
        """Calcola le proprietà geometriche della sezione ad L."""
        width = self.dimensions.get("width", 0)
        height = self.dimensions.get("height", 0)
        t_horizontal = self.dimensions.get("t_horizontal", 0)
        t_vertical = self.dimensions.get("t_vertical", 0)

        if any(x <= 0 for x in [width, height, t_horizontal, t_vertical]):
            raise ValueError("Dimensioni non valide per la sezione ad L")

        # Area
        self.properties.area = width * t_horizontal + (height - t_horizontal) * t_vertical

        # Centro di gravità
        area_horizontal = width * t_horizontal
        area_vertical = (height - t_horizontal) * t_vertical

        x_horizontal = width / 2
        y_horizontal = t_horizontal / 2

        x_vertical = t_vertical / 2
        y_vertical = t_horizontal + (height - t_horizontal) / 2

        self.properties.x_G = (
            area_horizontal * x_horizontal + area_vertical * x_vertical
        ) / self.properties.area
        self.properties.y_G = (
            area_horizontal * y_horizontal + area_vertical * y_vertical
        ) / self.properties.area

        # Momenti di inerzia (calcolo semplificato)
        # Questa è una semplificazione - il calcolo preciso richiederebbe formule più complesse
        ix_local = (t_horizontal * width**3) / 12 + (t_vertical * (height - t_horizontal) ** 3) / 12
        iy_local = (width * t_horizontal**3) / 12 + ((height - t_horizontal) * t_vertical**3) / 12
        ixy_local = 0.0

        # Applica rotazione se necessario
        if self.rotation_angle_deg != 0:
            angle_rad = math.radians(self.rotation_angle_deg)
            self.properties.Ix, self.properties.Iy, self.properties.Ixy = rotate_inertia(
                ix_local, iy_local, ixy_local, angle_rad
            )
        else:
            self.properties.Ix = ix_local
            self.properties.Iy = iy_local
            self.properties.Ixy = ixy_local

        # Proprietà shear
        kappa_y, kappa_z = self.get_default_shear_kappas()
        self.properties.kappa_y = kappa_y
        self.properties.kappa_z = kappa_z

        # Aree shear
        from ..services import compute_shear_areas

        self.properties.A_y, self.properties.A_z = compute_shear_areas(self)

        # Proprietà shear Qx, Qy
        self.properties.Qx = self.properties.area * self.properties.y_G
        self.properties.Qy = self.properties.area * self.properties.x_G

        # Core section (semplificato)
        self.properties.core_x = self.properties.Iy / (self.properties.area * (width / 2))
        self.properties.core_y = self.properties.Ix / (self.properties.area * (height / 2))


class CircularHollowSection(Section):
    """Sezione circolare cava (tubo)."""

    @property
    def section_type(self) -> str:
        return "CIRCULAR_HOLLOW"

    def _compute_geometric_properties(self):
        """Calcola le proprietà geometriche della sezione circolare cava."""
        outer_diameter = self.dimensions.get("outer_diameter", 0)
        thickness = self.dimensions.get("thickness", 0)

        if outer_diameter <= 0 or thickness <= 0:
            raise ValueError("Dimensioni non valide per la sezione circolare cava")

        inner_diameter = outer_diameter - 2 * thickness
        if inner_diameter < 0:
            raise ValueError("Spessore troppo grande rispetto al diametro esterno")

        r_out = outer_diameter / 2
        r_in = inner_diameter / 2

        # Area
        self.properties.area = math.pi * (r_out**2 - r_in**2)

        # Centro di gravità
        self.properties.x_G = r_out
        self.properties.y_G = r_out

        # Momenti di inerzia locali (cava = esterna - interna)
        ix_local = (math.pi / 4) * (r_out**4 - r_in**4)
        iy_local = ix_local
        ixy_local = 0.0

        # Applica rotazione (circolare non cambia, ma manteniamo coerenza)
        if self.rotation_angle_deg != 0:
            angle_rad = math.radians(self.rotation_angle_deg)
            self.properties.Ix, self.properties.Iy, self.properties.Ixy = rotate_inertia(
                ix_local, iy_local, ixy_local, angle_rad
            )
        else:
            self.properties.Ix = ix_local
            self.properties.Iy = iy_local
            self.properties.Ixy = ixy_local

        # Proprietà shear
        kappa_y, kappa_z = self.get_default_shear_kappas()
        self.properties.kappa_y = kappa_y
        self.properties.kappa_z = kappa_z

        # Aree shear
        from ..services import compute_shear_areas

        self.properties.A_y, self.properties.A_z = compute_shear_areas(self)

        # Proprietà shear Qx, Qy
        self.properties.Qx = self.properties.area * self.properties.y_G
        self.properties.Qy = self.properties.area * self.properties.x_G

        # Core section
        self.properties.core_x = r_out / 4
        self.properties.core_y = r_out / 4


class RectangularHollowSection(Section):
    """Sezione rettangolare cava."""

    @property
    def section_type(self) -> str:
        return "RECTANGULAR_HOLLOW"

    def _compute_geometric_properties(self):
        """Calcola le proprietà geometriche della sezione rettangolare cava."""
        width = self.dimensions.get("width", 0)
        height = self.dimensions.get("height", 0)
        thickness = self.dimensions.get("thickness", 0)

        if any(x <= 0 for x in [width, height, thickness]):
            raise ValueError("Dimensioni non valide per la sezione rettangolare cava")

        # Dimensioni interne
        inner_width = width - 2 * thickness
        inner_height = height - 2 * thickness

        if inner_width <= 0 or inner_height <= 0:
            raise ValueError("Spessore troppo grande rispetto alle dimensioni esterne")

        # Area
        area_outer = width * height
        area_inner = inner_width * inner_height
        self.properties.area = area_outer - area_inner

        # Centro di gravità
        self.properties.x_G = width / 2
        self.properties.y_G = height / 2

        # Momenti di inerzia (cava = esterna - interna)
        ix_local = (width * height**3 - inner_width * inner_height**3) / 12
        iy_local = (height * width**3 - inner_height * inner_width**3) / 12
        ixy_local = 0.0

        # Applica rotazione se necessario
        if self.rotation_angle_deg != 0:
            angle_rad = math.radians(self.rotation_angle_deg)
            self.properties.Ix, self.properties.Iy, self.properties.Ixy = rotate_inertia(
                ix_local, iy_local, ixy_local, angle_rad
            )
        else:
            self.properties.Ix = ix_local
            self.properties.Iy = iy_local
            self.properties.Ixy = ixy_local

        # Proprietà shear
        kappa_y, kappa_z = self.get_default_shear_kappas()
        self.properties.kappa_y = kappa_y
        self.properties.kappa_z = kappa_z

        # Aree shear
        from ..services import compute_shear_areas

        self.properties.A_y, self.properties.A_z = compute_shear_areas(self)

        # Proprietà shear Qx, Qy
        self.properties.Qx = self.properties.area * self.properties.y_G
        self.properties.Qy = self.properties.area * self.properties.x_G

        # Core section
        self.properties.core_x = self.properties.Iy / (self.properties.area * (width / 2))
        self.properties.core_y = self.properties.Ix / (self.properties.area * (height / 2))


class ISection(Section):
    """Sezione a I (doppia T)."""

    @property
    def section_type(self) -> str:
        return "I_SECTION"

    def _compute_geometric_properties(self):
        """Calcola le proprietà geometriche della sezione a I."""
        flange_width = self.dimensions.get("flange_width", 0)
        flange_thickness = self.dimensions.get("flange_thickness", 0)
        web_thickness = self.dimensions.get("web_thickness", 0)
        web_height = self.dimensions.get("web_height", 0)

        if any(x <= 0 for x in [flange_width, flange_thickness, web_thickness, web_height]):
            raise ValueError("Dimensioni non valide per la sezione a I")

        # Area componenti
        area_flange = 2 * flange_width * flange_thickness  # Due flange
        area_web = web_thickness * web_height
        self.properties.area = area_flange + area_web

        # Centro di gravità (asse y verticale attraverso il centro)
        self.properties.x_G = flange_width / 2
        self.properties.y_G = web_height / 2

        # Momenti di inerzia rispetto al centro di gravità
        # Flange superiore
        ix_flange_top = (flange_width * flange_thickness**3) / 12 + area_flange / 2 * (
            (web_height + flange_thickness) / 2
        ) ** 2
        # Flange inferiore
        ix_flange_bottom = (flange_width * flange_thickness**3) / 12 + area_flange / 2 * (
            (web_height + flange_thickness) / 2
        ) ** 2
        # Anima
        ix_web = (web_thickness * web_height**3) / 12

        ix_local = ix_flange_top + ix_flange_bottom + ix_web
        iy_local = (
            2 * (flange_thickness * flange_width**3) / 12 + (web_height * web_thickness**3) / 12
        )
        ixy_local = 0.0

        # Applica rotazione se necessario
        if self.rotation_angle_deg != 0:
            angle_rad = math.radians(self.rotation_angle_deg)
            self.properties.Ix, self.properties.Iy, self.properties.Ixy = rotate_inertia(
                ix_local, iy_local, ixy_local, angle_rad
            )
        else:
            self.properties.Ix = ix_local
            self.properties.Iy = iy_local
            self.properties.Ixy = ixy_local

        # Proprietà shear
        kappa_y, kappa_z = self.get_default_shear_kappas()
        self.properties.kappa_y = kappa_y
        self.properties.kappa_z = kappa_z

        # Aree shear
        from ..services import compute_shear_areas

        self.properties.A_y, self.properties.A_z = compute_shear_areas(self)

        # Proprietà shear Qx, Qy
        self.properties.Qx = self.properties.area * self.properties.y_G
        self.properties.Qy = self.properties.area * self.properties.x_G

        # Core section
        self.properties.core_x = self.properties.Iy / (self.properties.area * (flange_width / 2))
        self.properties.core_y = self.properties.Ix / (self.properties.area * (web_height / 2))


class PiSection(Section):
    """Sezione a Pi."""

    @property
    def section_type(self) -> str:
        return "PI_SECTION"

    def _compute_geometric_properties(self):
        """Calcola le proprietà geometriche della sezione a Pi."""
        # Implementazione semplificata - simile alla sezione I ma con flange più piccole
        flange_width = self.dimensions.get("flange_width", 0)
        flange_thickness = self.dimensions.get("flange_thickness", 0)
        web_thickness = self.dimensions.get("web_thickness", 0)
        web_height = self.dimensions.get("web_height", 0)
        t_horizontal = self.dimensions.get("t_horizontal", flange_thickness)

        if any(x <= 0 for x in [flange_width, flange_thickness, web_thickness, web_height]):
            raise ValueError("Dimensioni non valide per la sezione a Pi")

        # Per semplicità, tratta come sezione I con flange più piccole
        # Area
        area_flange = 2 * flange_width * t_horizontal
        area_web = web_thickness * web_height
        self.properties.area = area_flange + area_web

        # Centro di gravità
        self.properties.x_G = flange_width / 2
        self.properties.y_G = web_height / 2

        # Momenti di inerzia (semplificati)
        ix_local = (web_thickness * web_height**3) / 12 + 2 * (flange_width * t_horizontal**3) / 12
        iy_local = 2 * (t_horizontal * flange_width**3) / 12 + (web_height * web_thickness**3) / 12
        ixy_local = 0.0

        # Applica rotazione se necessario
        if self.rotation_angle_deg != 0:
            angle_rad = math.radians(self.rotation_angle_deg)
            self.properties.Ix, self.properties.Iy, self.properties.Ixy = rotate_inertia(
                ix_local, iy_local, ixy_local, angle_rad
            )
        else:
            self.properties.Ix = ix_local
            self.properties.Iy = iy_local
            self.properties.Ixy = ixy_local

        # Proprietà shear
        kappa_y, kappa_z = self.get_default_shear_kappas()
        self.properties.kappa_y = kappa_y
        self.properties.kappa_z = kappa_z

        # Aree shear
        from ..services import compute_shear_areas

        self.properties.A_y, self.properties.A_z = compute_shear_areas(self)

        # Proprietà shear Qx, Qy
        self.properties.Qx = self.properties.area * self.properties.y_G
        self.properties.Qy = self.properties.area * self.properties.x_G

        # Core section
        self.properties.core_x = self.properties.Iy / (self.properties.area * (flange_width / 2))
        self.properties.core_y = self.properties.Ix / (self.properties.area * (web_height / 2))


class InvertedTSection(Section):
    """Sezione a T invertita."""

    @property
    def section_type(self) -> str:
        return "INVERTED_T_SECTION"

    def _compute_geometric_properties(self):
        """Calcola le proprietà geometriche della sezione a T invertita."""
        flange_width = self.dimensions.get("flange_width", 0)
        flange_thickness = self.dimensions.get("flange_thickness", 0)
        web_thickness = self.dimensions.get("web_thickness", 0)
        web_height = self.dimensions.get("web_height", 0)

        if any(x <= 0 for x in [flange_width, flange_thickness, web_thickness, web_height]):
            raise ValueError("Dimensioni non valide per la sezione a T invertita")

        # Area componenti
        area_flange = flange_width * flange_thickness
        area_web = web_thickness * web_height
        self.properties.area = area_flange + area_web

        # Centro di gravità (rispetto alla cima dell'anima)
        y_flange = flange_thickness / 2
        self.properties.x_G = flange_width / 2
        self.properties.y_G = (
            area_flange * y_flange + area_web * (flange_thickness + web_height / 2)
        ) / self.properties.area

        # Momenti di inerzia locali rispetto al centro di gravità
        # Flangia
        ix_flange = (flange_width * flange_thickness**3) / 12 + area_flange * (
            y_flange - self.properties.y_G
        ) ** 2
        iy_flange = (flange_thickness * flange_width**3) / 12

        # Anima
        ix_web = (web_thickness * web_height**3) / 12 + area_web * (
            flange_thickness + web_height / 2 - self.properties.y_G
        ) ** 2
        iy_web = (web_height * web_thickness**3) / 12

        ix_local = ix_flange + ix_web
        iy_local = iy_flange + iy_web
        ixy_local = 0.0

        # Applica rotazione se necessario
        if self.rotation_angle_deg != 0:
            angle_rad = math.radians(self.rotation_angle_deg)
            self.properties.Ix, self.properties.Iy, self.properties.Ixy = rotate_inertia(
                ix_local, iy_local, ixy_local, angle_rad
            )
        else:
            self.properties.Ix = ix_local
            self.properties.Iy = iy_local
            self.properties.Ixy = ixy_local

        # Proprietà shear
        kappa_y, kappa_z = self.get_default_shear_kappas()
        self.properties.kappa_y = kappa_y
        self.properties.kappa_z = kappa_z

        # Aree shear
        from ..services import compute_shear_areas

        self.properties.A_y, self.properties.A_z = compute_shear_areas(self)

        # Proprietà shear Qx, Qy
        self.properties.Qx = self.properties.area * self.properties.y_G
        self.properties.Qy = self.properties.area * self.properties.x_G

        # Core section
        self.properties.core_x = self.properties.Iy / (self.properties.area * (flange_width / 2))
        self.properties.core_y = self.properties.Ix / (self.properties.area * (web_height / 2))


class CSection(Section):
    """Sezione a C."""

    @property
    def section_type(self) -> str:
        return "C_SECTION"

    def _compute_geometric_properties(self):
        """Calcola le proprietà geometriche della sezione a C."""
        width = self.dimensions.get("width", 0)
        height = self.dimensions.get("height", 0)
        thickness = self.dimensions.get("thickness", 0)

        if any(x <= 0 for x in [width, height, thickness]):
            raise ValueError("Dimensioni non valide per la sezione a C")

        # Area (semplificata: due flange + anima)
        area_flanges = 2 * width * thickness
        area_web = (height - 2 * thickness) * thickness
        self.properties.area = area_flanges + area_web

        # Centro di gravità (semplificato)
        self.properties.x_G = width / 2
        self.properties.y_G = height / 2

        # Momenti di inerzia (semplificati)
        ix_local = (thickness * width**3) / 12 + (thickness * (height - 2 * thickness) ** 3) / 12
        iy_local = 2 * (thickness * width**3) / 12 + ((height - 2 * thickness) * thickness**3) / 12
        ixy_local = 0.0

        # Applica rotazione se necessario
        if self.rotation_angle_deg != 0:
            angle_rad = math.radians(self.rotation_angle_deg)
            self.properties.Ix, self.properties.Iy, self.properties.Ixy = rotate_inertia(
                ix_local, iy_local, ixy_local, angle_rad
            )
        else:
            self.properties.Ix = ix_local
            self.properties.Iy = iy_local
            self.properties.Ixy = ixy_local

        # Proprietà shear
        kappa_y, kappa_z = self.get_default_shear_kappas()
        self.properties.kappa_y = kappa_y
        self.properties.kappa_z = kappa_z

        # Aree shear
        from ..services import compute_shear_areas

        self.properties.A_y, self.properties.A_z = compute_shear_areas(self)

        # Proprietà shear Qx, Qy
        self.properties.Qx = self.properties.area * self.properties.y_G
        self.properties.Qy = self.properties.area * self.properties.x_G

        # Core section
        self.properties.core_x = self.properties.Iy / (self.properties.area * (width / 2))
        self.properties.core_y = self.properties.Ix / (self.properties.area * (height / 2))


class VSection(Section):
    """Sezione a V."""

    @property
    def section_type(self) -> str:
        return "V_SECTION"

    def _compute_geometric_properties(self):
        """Calcola le proprietà geometriche della sezione a V."""
        # Implementazione semplificata per sezione a V
        width = self.dimensions.get("width", 0)
        height = self.dimensions.get("height", 0)
        thickness = self.dimensions.get("thickness", 0)

        if any(x <= 0 for x in [width, height, thickness]):
            raise ValueError("Dimensioni non valide per la sezione a V")

        # Area (semplificata come triangolo)
        self.properties.area = width * height / 2 * thickness  # Area volumetrica semplificata

        # Centro di gravità (semplificato)
        self.properties.x_G = width / 3
        self.properties.y_G = height / 3

        # Momenti di inerzia (semplificati)
        ix_local = (thickness * width * height**3) / 36  # Per triangolo
        iy_local = (thickness * height * width**3) / 48
        ixy_local = 0.0

        # Applica rotazione se necessario
        if self.rotation_angle_deg != 0:
            angle_rad = math.radians(self.rotation_angle_deg)
            self.properties.Ix, self.properties.Iy, self.properties.Ixy = rotate_inertia(
                ix_local, iy_local, ixy_local, angle_rad
            )
        else:
            self.properties.Ix = ix_local
            self.properties.Iy = iy_local
            self.properties.Ixy = ixy_local

        # Proprietà shear
        kappa_y, kappa_z = self.get_default_shear_kappas()
        self.properties.kappa_y = kappa_y
        self.properties.kappa_z = kappa_z

        # Aree shear
        from ..services import compute_shear_areas

        self.properties.A_y, self.properties.A_z = compute_shear_areas(self)

        # Proprietà shear Qx, Qy
        self.properties.Qx = self.properties.area * self.properties.y_G
        self.properties.Qy = self.properties.area * self.properties.x_G

        # Core section
        self.properties.core_x = self.properties.Iy / (self.properties.area * (width / 2))
        self.properties.core_y = self.properties.Ix / (self.properties.area * (height / 2))


class InvertedVSection(Section):
    """Sezione a V invertita."""

    @property
    def section_type(self) -> str:
        return "INVERTED_V_SECTION"

    def _compute_geometric_properties(self):
        """Calcola le proprietà geometriche della sezione a V invertita."""
        # Implementazione semplificata per sezione a V invertita
        width = self.dimensions.get("width", 0)
        height = self.dimensions.get("height", 0)
        thickness = self.dimensions.get("thickness", 0)

        if any(x <= 0 for x in [width, height, thickness]):
            raise ValueError("Dimensioni non valide per la sezione a V invertita")

        # Area (semplificata come triangolo)
        self.properties.area = width * height / 2 * thickness

        # Centro di gravità (semplificato)
        self.properties.x_G = width / 3
        self.properties.y_G = 2 * height / 3

        # Momenti di inerzia (semplificati)
        ix_local = (thickness * width * height**3) / 36
        iy_local = (thickness * height * width**3) / 48
        ixy_local = 0.0

        # Applica rotazione se necessario
        if self.rotation_angle_deg != 0:
            angle_rad = math.radians(self.rotation_angle_deg)
            self.properties.Ix, self.properties.Iy, self.properties.Ixy = rotate_inertia(
                ix_local, iy_local, ixy_local, angle_rad
            )
        else:
            self.properties.Ix = ix_local
            self.properties.Iy = iy_local
            self.properties.Ixy = ixy_local

        # Proprietà shear
        kappa_y, kappa_z = self.get_default_shear_kappas()
        self.properties.kappa_y = kappa_y
        self.properties.kappa_z = kappa_z

        # Aree shear
        from ..services import compute_shear_areas

        self.properties.A_y, self.properties.A_z = compute_shear_areas(self)

        # Proprietà shear Qx, Qy
        self.properties.Qx = self.properties.area * self.properties.y_G
        self.properties.Qy = self.properties.area * self.properties.x_G

        # Core section
        self.properties.core_x = self.properties.Iy / (self.properties.area * (width / 2))
        self.properties.core_y = self.properties.Ix / (self.properties.area * (height / 2))
