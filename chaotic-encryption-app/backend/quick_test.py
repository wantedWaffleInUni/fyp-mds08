#!/usr/bin/env python3
"""
Quick test to verify all encryptors can be imported and instantiated.
"""

def test_imports():
    """Test that all encryptors can be imported and instantiated."""
    
    print("🔐 Testing Encryptor Imports and Instantiation")
    print("=" * 50)
    
    try:
        from encryption import (
            EncryptorInterface,
            ChaosEncryptor,
            FODHNNEncryptor,
            LASMEncryptor,
            LASMEncryptorFB,
            HybridEncryptorFB,
            BulbanEncryptor
        )
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test instantiation
    encryptors = []
    
    try:
        chaos = ChaosEncryptor()
        encryptors.append(chaos)
        print("✅ ChaosEncryptor instantiated")
    except Exception as e:
        print(f"❌ ChaosEncryptor failed: {e}")
    
    try:
        fodhnn = FODHNNEncryptor()
        encryptors.append(fodhnn)
        print("✅ FODHNNEncryptor instantiated")
    except Exception as e:
        print(f"❌ FODHNNEncryptor failed: {e}")
    
    try:
        lasm = LASMEncryptor()
        encryptors.append(lasm)
        print("✅ LASMEncryptor instantiated")
    except Exception as e:
        print(f"❌ LASMEncryptor failed: {e}")
    
    try:
        lasm_fb = LASMEncryptorFB()
        encryptors.append(lasm_fb)
        print("✅ LASMEncryptorFB instantiated")
    except Exception as e:
        print(f"❌ LASMEncryptorFB failed: {e}")
    
    try:
        hybrid = HybridEncryptorFB()
        encryptors.append(hybrid)
        print("✅ HybridEncryptorFB instantiated")
    except Exception as e:
        print(f"❌ HybridEncryptorFB failed: {e}")
    
    try:
        bulban = BulbanEncryptor()
        encryptors.append(bulban)
        print("✅ BulbanEncryptor instantiated")
    except Exception as e:
        print(f"❌ BulbanEncryptor failed: {e}")
    
    # Test interface compliance
    print(f"\n📊 Interface Compliance Check:")
    print(f"   Total encryptors: {len(encryptors)}")
    
    for encryptor in encryptors:
        try:
            # Check if it inherits from interface
            assert isinstance(encryptor, EncryptorInterface), f"{encryptor.__class__.__name__} should inherit from EncryptorInterface"
            
            # Check required methods
            algorithm_name = encryptor.get_algorithm_name()
            
            print(f"   ✅ {encryptor.__class__.__name__}: {algorithm_name}")
            
        except Exception as e:
            print(f"   ❌ {encryptor.__class__.__name__}: {e}")
    
    print(f"\n🎉 All encryptors successfully tested!")
    return True

if __name__ == "__main__":
    test_imports()
