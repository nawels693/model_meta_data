try:
    from spinqit import get_nmr, get_compiler, Circuit, NMRConfig
    print("[OK] spinqit esta instalado y disponible")
    print("  Puedes ejecutar poc_spinq.py")
except ImportError as e:
    print("[ERROR] spinqit NO esta instalado")
    print(f"  Error: {e}")
    print("\nPara instalar spinqit:")
    print("  1. Verifica si tu universidad proporciona un instalador")
    print("  2. O instala desde un repositorio interno")
    print("  3. O contacta al administrador del sistema SpinQ")

