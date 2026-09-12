// Safety check to see if lucide cdn is actually loaded
if (window.lucide) {
    lucide.createIcons();
}

const tabLogin = document.getElementById("tab-login");
const tabRegister = document.getElementById("tab-register");
const formLogin = document.getElementById("form-login");
const formRegister = document.getElementById("form-register");

tabRegister.addEventListener("click", () => {
    tabRegister.classList.add("active-tab");
    tabRegister.classList.remove("text-secondary");
    tabLogin.classList.remove("active-tab");
    tabLogin.classList.add("text-secondary");

    formLogin.classList.add("d-none");
    formRegister.classList.remove("d-none");

    lucide.createIcons();
});

tabLogin.addEventListener("click", () => {
    tabLogin.classList.add("active-tab");
    tabLogin.classList.remove("text-secondary");
    tabRegister.classList.remove("active-tab");
    tabRegister.classList.add("text-secondary");

    formRegister.classList.add("d-none");
    formLogin.classList.remove("d-none");

    lucide.createIcons();
});


const regFullname = document.getElementById("reg-fullname");
const errFullname = document.getElementById("err-fullname");

const regEmail = document.getElementById("reg-email");
const errEmail = document.getElementById("err-email");

const regPassword = document.getElementById("reg-password");
const errPassword = document.getElementById("err-password");

const regConfirm = document.getElementById("reg-confirm");
const errConfirm = document.getElementById("err-confirm");

const regLocation = document.getElementById("reg-location");
const errLocation = document.getElementById("err-location");

const regDob = document.getElementById("reg-dob");
const errDob = document.getElementById("err-dob");

const regMobile = document.getElementById("reg-mobile");
const errMobile = document.getElementById("err-mobile");

const registerBtn = document.getElementById("registerBtn");

const loginPassword = document.getElementById("login-password");

const toggleLoginPasswordBtn = document.getElementById("toggleLoginPasswordBtn");
const toggleRegPasswordBtn = document.getElementById("toggleRegPasswordBtn");
const toggleConfirmPasswordBtn = document.getElementById("toggleConfirmPasswordBtn");

// Show password buttons event listeners
toggleLoginPasswordBtn.addEventListener("click", () => { togglePassword(loginPassword, toggleLoginPasswordBtn); });
toggleRegPasswordBtn.addEventListener("click", () => { togglePassword(regPassword, toggleRegPasswordBtn); });
toggleConfirmPasswordBtn.addEventListener("click", () => { togglePassword(regConfirm, toggleConfirmPasswordBtn); });

// Reusable function for show Password functionality in 3 password fields
function togglePassword(passwordField, buttonElement) {
    const isPassword = passwordField.type === "password";
    passwordField.type = (isPassword) ? "text" : "password";
    
    buttonElement.innerHTML = (isPassword) ? `<i data-lucide="eye-off" width="18"></i>` : `<i data-lucide="eye" width="18"></i>`;
    lucide.createIcons();
}

function validateFullname() {
    if (regFullname.value === "") {
        errFullname.classList.add("d-none");
        return false;
    }

    if (regFullname.value.trim().length < 3) {
        errFullname.classList.remove("d-none");
        return false;
    }
    errFullname.classList.add("d-none");
    return true;
}

// ^ and $ are anchors ensuring the entire string matches the pattern from start to finish.
// [a-zA-Z0-9._%+-]+ matches one or more valid username characters (letters, numbers, and common symbols).
// @ matches the literal "@" separator.
// [a-zA-Z0-9.-]+ matches the domain name (e.g., "gmail" or "outlook"), allowing letters, numbers, dots, and hyphens.
// \. matches the literal dot before the Top-Level Domain (TLD).
// [a-zA-Z]{2,} ensures the TLD (e.g., "com", "edu") contains only letters and is at least 2 characters long.
const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
function validateEmail() {
    const email = regEmail.value.trim();
    
    // Everytime a field changes all fields are validated so to prevent all fields from becoming red, error is only displayed if the field
    // isn't empty
    if (email==="") {
        errPassword.classList.add("d-none");
        return false;
    }

    if (!emailRegex.test(email)) {
        errEmail.classList.remove("d-none");
        return false;
    }

    errEmail.classList.add("d-none");
    return true;
}

// ^ and $ are anchors ensuring the pattern matches the string from start to finish.
// (?=.*[A-Za-z]) is a positive lookahead assertion: it scans for at least one letter without moving the match cursor.
// (?=.*\d) is a second lookahead assertion: it ensures at least one digit is present before proceeding.
// [A-Za-z\d@$!%*?&.] defines the allowed character set (alphanumeric + specific symbols).
// {6,} enforces a minimum length of 6 characters for the entire string.
const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&.]{6,}$/;
function validatePassword() {
    const pwd = regPassword.value;

    if (pwd==="") {
        errPassword.classList.add("d-none");
        return false;
    }

    if (!passwordRegex.test(pwd)) {
        errPassword.classList.remove("d-none");
        return false;
    }

    errPassword.classList.add("d-none");
    return true;
}

function validateConfirmPassword() {
    if (regConfirm.value === "") {
        errConfirm.classList.add("d-none");
        return false;
    }

    if (regConfirm.value !== regPassword.value) {
        errConfirm.classList.remove("d-none");
        return false;
    }

    errConfirm.classList.add("d-none");
    return true;
}

function validateLocation() {
    if (regLocation.value === "") {
        errLocation.classList.add("d-none");
        return false;
    }

    // Split and clean
    const parts = regLocation.value.split(",").map(part => part.trim());

    // Ensure exactly 2 parts AND both parts have text => District, State
    if (parts.length!=2 || parts[0]==="" || parts[1]==="") {
        errLocation.classList.remove("d-none");
        return false;
    }

    errLocation.classList.add("d-none");
    return true;
}

function validateDOB() {
    if (!regDob.value) {
        errDob.classList.add("d-none");
        return false;
    }

    const dob = new Date(regDob.value);
    const today = new Date();

    if (dob > today) {
        errDob.classList.remove("d-none");
        errDob.innerText = "Date of birth cannot be in future";
        return false;
    }

    let age = today.getFullYear() - dob.getFullYear();
    const m = today.getMonth() - dob.getMonth();

    if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
        age--;
    }

    if (age < 13) {
        errDob.classList.remove("d-none");
        errDob.innerText = "You must be at least 13 years old";
        return false;
    }

    errDob.classList.add("d-none");
    return true;
}

function validateMobile() {
    const mobile = regMobile.value.trim();

    if (mobile === "") {
        errMobile.classList.add("d-none");
        return false;
    }

    // ^[6-9] ensures the 10-digit mobile number starts with a valid Indian prefix (6, 7, 8, or 9).
    // \d{9}$ ensures exactly 9 more digits follow, totaling 10 digits without extra trailing characters.
    if (!/^[6-9]\d{9}$/.test(mobile)) {
        errMobile.classList.remove("d-none");
        return false;
    }

    errMobile.classList.add("d-none");
    return true;
}


function checkRegisterForm() {
    if (
        validateFullname() &&
        validateEmail() &&
        validatePassword() &&
        validateConfirmPassword() &&
        validateLocation() &&
        validateDOB() &&
        validateMobile()
    ) {
        registerBtn.disabled = false;
    } else {
        registerBtn.disabled = true;
    }
}

setTimeout(() => {
   document.querySelectorAll('.alert').forEach(a => a.remove());
}, 3000);   