#!/usr/bin/env python
"""
Demo script to verify Matplotlib integration in RD2229.

This script demonstrates that matplotlib is properly installed and integrated
for graphical representation of sections and verification tables.

Run with: python demo_matplotlib_integration.py
"""

import sys
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for CI/testing
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import numpy as np


def demo_basic_matplotlib():
    """Demonstrate basic matplotlib functionality."""
    print("=" * 70)
    print("Demo 1: Basic Matplotlib Functionality")
    print("=" * 70)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_title('RD2229 - Matplotlib Integration Demo', fontsize=14, fontweight='bold')
    
    # Draw a simple rectangular section
    rect = Rectangle((0, 0), 30, 50, fill=False, edgecolor='blue', linewidth=2)
    ax.add_patch(rect)
    
    # Add centroid
    cx, cy = 15, 25
    ax.plot(cx, cy, 'ro', markersize=10, label='Baricentro')
    ax.text(cx + 1, cy, ' Baricentro', fontsize=10, va='center')
    
    # Add dimensions
    ax.annotate('', xy=(0, -3), xytext=(30, -3),
                arrowprops=dict(arrowstyle='<->', color='black'))
    ax.text(15, -5, 'b = 30 cm', ha='center', fontsize=9)
    
    ax.annotate('', xy=(-3, 0), xytext=(-3, 50),
                arrowprops=dict(arrowstyle='<->', color='black'))
    ax.text(-6, 25, 'h = 50 cm', ha='center', va='center', rotation=90, fontsize=9)
    
    ax.set_xlim(-10, 40)
    ax.set_ylim(-10, 60)
    ax.set_xlabel('Larghezza (cm)', fontsize=10)
    ax.set_ylabel('Altezza (cm)', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right')
    ax.set_aspect('equal')
    
    output_file = '/tmp/matplotlib_demo_1.png'
    plt.savefig(output_file, dpi=100, bbox_inches='tight')
    print(f"✓ Plot saved to: {output_file}")
    plt.close()
    print()


def demo_section_visualization():
    """Demonstrate section visualization similar to verification table needs."""
    print("=" * 70)
    print("Demo 2: Section Visualization for Verification Table")
    print("=" * 70)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Sezioni per Verifica Strutturale', fontsize=14, fontweight='bold')
    
    # Left: Rectangular section with reinforcement
    ax1.set_title('Sezione Rettangolare con Armatura')
    rect = Rectangle((0, 0), 30, 50, fill=True, facecolor='lightgray', 
                     edgecolor='black', linewidth=2)
    ax1.add_patch(rect)
    
    # Add reinforcement bars (simplified)
    # Top bars
    for i, x in enumerate([5, 15, 25]):
        ax1.plot(x, 45, 'ko', markersize=8, markerfacecolor='red')
    
    # Bottom bars
    for i, x in enumerate([5, 15, 25]):
        ax1.plot(x, 5, 'ko', markersize=8, markerfacecolor='red')
    
    ax1.set_xlim(-5, 35)
    ax1.set_ylim(-5, 55)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('b = 30 cm')
    ax1.set_ylabel('h = 50 cm')
    
    # Right: Circular section
    ax2.set_title('Sezione Circolare')
    circle = Circle((20, 20), 15, fill=True, facecolor='lightgray',
                   edgecolor='black', linewidth=2)
    ax2.add_patch(circle)
    
    # Add reinforcement in circular pattern
    n_bars = 8
    for i in range(n_bars):
        angle = 2 * np.pi * i / n_bars
        x = 20 + 12 * np.cos(angle)
        y = 20 + 12 * np.sin(angle)
        ax2.plot(x, y, 'ko', markersize=8, markerfacecolor='red')
    
    # Centroid
    ax2.plot(20, 20, 'r+', markersize=12, markeredgewidth=2)
    
    ax2.set_xlim(0, 40)
    ax2.set_ylim(0, 40)
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('D = 30 cm')
    
    output_file = '/tmp/matplotlib_demo_2.png'
    plt.savefig(output_file, dpi=100, bbox_inches='tight')
    print(f"✓ Plot saved to: {output_file}")
    plt.close()
    print()


def demo_verification_results():
    """Demonstrate results visualization for verification calculations."""
    print("=" * 70)
    print("Demo 3: Verification Results Visualization")
    print("=" * 70)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title('Andamento Tensioni - Verifica a Flessione', 
                 fontsize=14, fontweight='bold')
    
    # Simulate stress distribution
    height = 50
    y = np.linspace(0, height, 100)
    
    # Compression zone (top)
    compression = np.where(y > 30, (y - 30) * 0.5, 0)
    
    # Tension zone (bottom)
    tension = np.where(y < 30, -(30 - y) * 0.6, 0)
    
    # Combined stress
    stress = compression + tension
    
    # Plot section outline
    ax.plot([0, 0], [0, height], 'k-', linewidth=2, label='Sezione')
    
    # Plot stress distribution
    ax.fill_betweenx(y, 0, stress, where=(stress >= 0), 
                     color='blue', alpha=0.3, label='Compressione')
    ax.fill_betweenx(y, 0, stress, where=(stress < 0), 
                     color='red', alpha=0.3, label='Trazione')
    ax.plot(stress, y, 'k-', linewidth=1.5)
    
    # Neutral axis
    ax.axhline(y=30, color='green', linestyle='--', linewidth=2, 
               label='Asse Neutro')
    
    ax.set_xlabel('Tensione (kg/cm²)', fontsize=11)
    ax.set_ylabel('Altezza Sezione (cm)', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best')
    ax.set_ylim(0, height)
    
    output_file = '/tmp/matplotlib_demo_3.png'
    plt.savefig(output_file, dpi=100, bbox_inches='tight')
    print(f"✓ Plot saved to: {output_file}")
    plt.close()
    print()


def verify_installation():
    """Verify that all components are properly installed."""
    print("=" * 70)
    print("Matplotlib Installation Verification")
    print("=" * 70)
    print()
    
    try:
        import matplotlib
        print(f"✓ Matplotlib version: {matplotlib.__version__}")
    except ImportError as e:
        print(f"✗ Matplotlib import failed: {e}")
        return False
    
    try:
        import pandas
        print(f"✓ Pandas version: {pandas.__version__}")
    except ImportError as e:
        print(f"✗ Pandas import failed: {e}")
        return False
    
    try:
        import numpy
        print(f"✓ NumPy version: {numpy.__version__}")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    print(f"✓ Python version: {sys.version.split()[0]}")
    print()
    
    # Check RD2229 package
    try:
        import subprocess
        result = subprocess.run(['pip', 'show', 'RD2229'], 
                              capture_output=True, text=True)
        if 'Version: 0.0.1' in result.stdout:
            print("✓ RD2229 package installed in editable mode")
            for line in result.stdout.split('\n'):
                if line.startswith('Location:'):
                    print(f"  {line}")
                    break
        else:
            print("⚠ RD2229 package status unclear")
    except Exception as e:
        print(f"⚠ Could not verify RD2229 package: {e}")
    
    print()
    return True


def main():
    """Main demonstration function."""
    print()
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  RD2229 - Matplotlib Integration Demonstration  ".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print()
    
    # Verify installation
    if not verify_installation():
        print("Installation verification failed!")
        return 1
    
    # Run demonstrations
    try:
        demo_basic_matplotlib()
        demo_section_visualization()
        demo_verification_results()
        
        print("=" * 70)
        print("SUCCESS: All demonstrations completed successfully!")
        print("=" * 70)
        print()
        print("Matplotlib is properly integrated and ready for use in:")
        print("  • Section visualization (gui/section_gui.py)")
        print("  • Verification table graphical representation")
        print("  • Stress distribution plots")
        print("  • Results visualization")
        print()
        print("Generated plots are saved in /tmp/matplotlib_demo_*.png")
        print()
        return 0
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
