#!/usr/bin/env python3
"""
Script de prueba para validar las expresiones regulares del cambio de contraseñas.
"""

import re

def test_password_patterns():
    """Prueba los patrones de regex para validación de contraseñas."""
    
    print("🔍 Probando expresiones regulares para validación de contraseñas...")
    
    # Patrones que se usan en el diálogo
    lowercase_pattern = r'[a-z]'
    uppercase_pattern = r'[A-Z]' 
    digit_pattern = r'\d'
    special_pattern = r'[!@#$%^&*()_+=\-\[\]{};\':"\\|,.<>/?]'
    
    # Contraseñas de prueba
    test_passwords = [
        "admin123",
        "Admin123!",
        "MiContraseña2024@",
        "abc123",
        "PASSWORD123",
        "Test@2024#Special",
        "SimplePassword",
        "123456789",
        "!@#$%^&*()"
    ]
    
    print("\n📋 Resultados de validación:")
    print("-" * 60)
    
    for password in test_passwords:
        print(f"\n🔑 Contraseña: '{password}'")
        
        # Validar cada patrón
        has_lower = bool(re.search(lowercase_pattern, password))
        has_upper = bool(re.search(uppercase_pattern, password))
        has_digit = bool(re.search(digit_pattern, password))
        has_special = bool(re.search(special_pattern, password))
        
        print(f"  ✓ Minúsculas: {'Sí' if has_lower else 'No'}")
        print(f"  ✓ Mayúsculas: {'Sí' if has_upper else 'No'}")
        print(f"  ✓ Números: {'Sí' if has_digit else 'No'}")
        print(f"  ✓ Símbolos: {'Sí' if has_special else 'No'}")
        
        # Calcular puntuación
        score = sum([has_lower, has_upper, has_digit, has_special])
        if len(password) >= 8:
            score += 1
            
        print(f"  📊 Puntuación: {score}/5")
        
        if score <= 1:
            strength = "Muy débil"
        elif score <= 2:
            strength = "Débil"
        elif score <= 3:
            strength = "Regular"
        elif score <= 4:
            strength = "Buena"
        else:
            strength = "Muy fuerte"
            
        print(f"  🛡️ Fortaleza: {strength}")

def test_special_characters():
    """Prueba caracteres especiales específicos."""
    
    print("\n\n🎯 Probando caracteres especiales específicos...")
    print("-" * 60)
    
    special_chars = "!@#$%^&*()_+=-[]{};\':\"\\|,.<>/?"
    pattern = r'[!@#$%^&*()_+=\-\[\]{};\':"\\|,.<>/?]'
    
    for char in special_chars:
        try:
            match = bool(re.search(pattern, char))
            print(f"'{char}': {'✓' if match else '✗'}")
        except Exception as e:
            print(f"'{char}': ERROR - {e}")

if __name__ == "__main__":
    try:
        test_password_patterns()
        test_special_characters()
        print("\n✅ Todas las pruebas completadas exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()