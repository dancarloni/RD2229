"""
Verification engine that integrates calculation core with configuration system.

This module provides the main interface for performing structural verifications
using the .jsoncode configuration system and verification core calculations.
"""

from __future__ import annotations

from typing import Optional
import logging

from core.verification_core import (
    VerificationType,
    SectionGeometry,
    ReinforcementLayer,
    MaterialProperties,
    LoadCase,
    NeutralAxis,
    StressState,
    VerificationResult,
    calculate_neutral_axis_simple_bending,
    calculate_stresses_simple_bending,
    verify_allowable_stresses,
)

try:
    from config.calculation_codes_loader import load_code, get_safety_coefficients, get_stress_limits
    from config.historical_materials_loader import get_concrete_properties, get_steel_properties
except ImportError:
    # Fallback if config modules not available
    load_code = None
    get_concrete_properties = None
    get_steel_properties = None

logger = logging.getLogger(__name__)


class VerificationEngine:
    """Main verification engine."""
    
    def __init__(self, calculation_code: str = "TA"):
        """
        Initialize verification engine.
        
        Args:
            calculation_code: Calculation code ("TA", "SLU", "SLE")
        """
        self.calculation_code = calculation_code.upper()
        self.config = None
        
        # Load configuration if available
        if load_code:
            try:
                self.config = load_code(self.calculation_code)
                logger.info(f"Loaded configuration for {self.calculation_code}")
            except Exception as e:
                logger.warning(f"Could not load configuration: {e}")
    
    def get_material_properties(
        self,
        concrete_class: str,
        steel_type: str,
        material_source: str = "RD2229"
    ) -> MaterialProperties:
        """
        Get material properties from configuration.
        
        Args:
            concrete_class: Concrete class (e.g., "R160", "C25_30")
            steel_type: Steel type (e.g., "FeB38k", "B450C")
            material_source: Material source ("RD2229", "NTC2018", etc.)
        
        Returns:
            Material properties
        """
        if get_concrete_properties and get_steel_properties:
            try:
                concrete = get_concrete_properties(material_source, concrete_class)
                steel = get_steel_properties(material_source, steel_type)
                
                # Extract properties based on source
                if material_source == "RD2229":
                    fck = concrete.get('sigma_c28', 160.0)
                    Ec = concrete.get('Ec', 250000.0)
                    fyk = steel.get('sigma_sn', 3800.0)
                    Es = steel.get('Es', 2100000.0)
                else:  # NTC2008/2018
                    fck = concrete.get('fck', 25.0)
                    Ec = concrete.get('Ecm', 31000.0)
                    fyk = steel.get('fyk', 450.0)
                    Es = steel.get('Es', 200000.0)
                
                return MaterialProperties(fck=fck, Ec=Ec, fyk=fyk, Es=Es)
            
            except Exception as e:
                logger.warning(f"Could not load material properties: {e}")
        
        # Default fallback
        return MaterialProperties(fck=160.0, Ec=250000.0, fyk=3800.0, Es=2100000.0)
    
    def get_allowable_stresses(
        self,
        material: MaterialProperties
    ) -> tuple[float, float]:
        """
        Get allowable stresses from configuration.
        
        Args:
            material: Material properties
        
        Returns:
            Tuple of (sigma_c_adm, sigma_s_adm)
        """
        if self.calculation_code == "TA":
            # For TA: σ_c,adm = 0.5 × σ_c,28
            sigma_c_adm = 0.5 * material.fck
            # For steel: σ_s,adm = σ_sn / 2.0 (assuming safety factor of 2)
            sigma_s_adm = material.fyk / 2.0 if material.fyk > 0 else 1900.0
        
        elif self.calculation_code == "SLU":
            # For SLU: use safety factors from config
            gamma_c = 1.5
            gamma_s = 1.15
            
            if self.config:
                try:
                    coeffs = self.config.get('safety_coefficients', {})
                    gamma_c = coeffs.get('gamma_c', {}).get('value', 1.5)
                    gamma_s = coeffs.get('gamma_s', {}).get('value', 1.15)
                except Exception:
                    pass
            
            sigma_c_adm = 0.85 * material.fck / gamma_c
            sigma_s_adm = material.fyk / gamma_s if material.fyk > 0 else 391.0
        
        else:  # SLE
            # For SLE: σ_c ≤ 0.6 × fck (characteristic)
            sigma_c_adm = 0.6 * material.fck
            sigma_s_adm = 0.8 * material.fyk if material.fyk > 0 else 360.0
        
        return sigma_c_adm, sigma_s_adm
    
    def perform_verification(
        self,
        section: SectionGeometry,
        reinforcement_tensile: ReinforcementLayer,
        reinforcement_compressed: ReinforcementLayer,
        material: MaterialProperties,
        loads: LoadCase,
        frc_material: "Optional[object]" = None,
        frc_area: float = 0.0,
    ) -> VerificationResult:
        """
        Perform complete structural verification.
        
        Args:
            section: Section geometry
            reinforcement_tensile: Tensile reinforcement
            reinforcement_compressed: Compressed reinforcement
            material: Material properties
            loads: Load case
        
        Returns:
            Verification result
        """
        # Determine verification type
        verif_type = loads.get_verification_type()
        
        # Get allowable stresses
        sigma_c_adm, sigma_s_adm = self.get_allowable_stresses(material)
        
        # Initialize result
        neutral_axis = NeutralAxis()
        stress_state = StressState()
        
        # Perform calculation based on verification type
        if verif_type in [VerificationType.BENDING_SIMPLE, VerificationType.AXIAL_BENDING_SIMPLE]:
            # Simple bending or axial+bending
            moment = loads.Mx if abs(loads.Mx) > abs(loads.My) else loads.My
            
            # Calculate neutral axis
            neutral_axis = calculate_neutral_axis_simple_bending(
                section=section,
                reinforcement_tensile=reinforcement_tensile,
                reinforcement_compressed=reinforcement_compressed,
                material=material,
                method=self.calculation_code
            )
            
            # Calculate stresses (pass through optional FRC parameters)
            stress_state = calculate_stresses_simple_bending(
                section=section,
                reinforcement_tensile=reinforcement_tensile,
                reinforcement_compressed=reinforcement_compressed,
                material=material,
                moment=moment,
                neutral_axis=neutral_axis,
                method=self.calculation_code,
                frc_material=frc_material,
                frc_area=frc_area,
            )
        
        elif verif_type == VerificationType.BENDING_DEVIATED:
            # Deviated bending - future implementation
            logger.warning("Deviated bending not yet fully implemented")
        
        elif verif_type == VerificationType.SHEAR:
            # Shear verification - future implementation
            logger.warning("Shear verification not yet fully implemented")
        
        elif verif_type == VerificationType.TORSION:
            # Torsion verification - future implementation
            logger.warning("Torsion verification not yet fully implemented")
        
        else:
            logger.warning(f"Verification type {verif_type} not yet implemented")
        
        # Verify stresses
        is_verified, util_concrete, util_steel, messages = verify_allowable_stresses(
            stress_state=stress_state,
            material=material,
            sigma_c_adm=sigma_c_adm,
            sigma_s_adm=sigma_s_adm
        )
        
        # Create result
        result = VerificationResult(
            verification_type=verif_type,
            neutral_axis=neutral_axis,
            stress_state=stress_state,
            utilization_concrete=util_concrete,
            utilization_steel=util_steel,
            is_verified=is_verified,
            messages=messages
        )
        
        return result


def create_verification_engine(calculation_code: str = "TA") -> VerificationEngine:
    """
    Create a verification engine instance.
    
    Args:
        calculation_code: Calculation code ("TA", "SLU", "SLE")
    
    Returns:
        Verification engine
    """
    return VerificationEngine(calculation_code=calculation_code)
