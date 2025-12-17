// Password Strength Indicator
// يقيس قوة كلمة المرور ويعرض مؤشر بصري

document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    const passwordStrength = document.getElementById('password-strength');
    const passwordText = document.getElementById('password-text');

    // التحقق من وجود العناصر
    if (!passwordInput || !passwordStrength || !passwordText) {
        return;
    }

    passwordInput.addEventListener('input', function() {
        const password = this.value;
        const strength = checkPasswordStrength(password);
        
        // إزالة جميع الكلاسات
        passwordStrength.classList.remove('password-weak', 'password-medium', 'password-strong');
        
        // إذا كانت خانة كلمة المرور فارغة
        if (password.length === 0) {
            passwordText.textContent = '';
            return;
        }
        
        // إضافة الكلاس المناسب حسب القوة
        if (strength === 1) {
            passwordStrength.classList.add('password-weak');
            passwordText.textContent = 'Weak password - كلمة مرور ضعيفة';
            passwordText.style.color = '#f44336';
        } else if (strength === 2) {
            passwordStrength.classList.add('password-medium');
            passwordText.textContent = 'Medium strength - قوة متوسطة';
            passwordText.style.color = '#ff9800';
        } else {
            passwordStrength.classList.add('password-strong');
            passwordText.textContent = 'Strong password - كلمة مرور قوية';
            passwordText.style.color = '#4caf50';
        }
    });
});

/**
 * فحص قوة كلمة المرور
 * @param {string} password - كلمة المرور المراد فحصها
 * @returns {number} - مستوى القوة (1=ضعيفة، 2=متوسطة، 3=قوية)
 */
function checkPasswordStrength(password) {
    let strength = 0;
    
    // فحص الطول
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    
    // فحص الحروف الصغيرة والكبيرة
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) {
        strength++;
    }
    
    // فحص الأرقام
    if (/\d/.test(password)) {
        strength++;
    }
    
    // فحص الرموز الخاصة
    if (/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/`~]/.test(password)) {
        strength++;
    }
    
    // تحديد مستوى القوة النهائي
    if (strength <= 2) return 1; // ضعيفة
    if (strength <= 4) return 2; // متوسطة
    return 3; // قوية
}
