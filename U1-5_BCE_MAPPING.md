# U1-5 BCE Mapping

## Register

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `RegisterPage` | [templates/auth.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/auth.html), [static/auth.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/auth.js) | Register form inputs for `username`, `email`, `password`, `code`; `registerForm submit`; `sendCodeButton click` |
| `AuthController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `RequestVerificationCode()`, `ValidationVerificationCode()`, `CreateAccount()` |
| `UserAccount` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `CreateUser()`, `SaveUser()` |
| `EmailVerification` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GenerateCode()`, `StoreCode()`, `CheckCode()` |

## Login

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `LoginPage` | [templates/auth.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/auth.html), [static/auth.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/auth.js) | Login form inputs for `email`, `password`; `loginForm submit`; login result display via `setMessage()` |
| `AuthController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidateCredentials()`, `Login()`, `CreateSession()` |
| `UserAccount` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetUserByEmail()`, `CheckPassword()` |
| `UserSession` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `CreateSession()`, `StoreSession()` |

## Logout

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `DashboardPage` | [templates/index.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/index.html), [templates/about.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/about.html) | User dropdown `Log Out` entry |
| `SessionController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `Logout()`, `TerminateSession()`, `ClearAuthentication()` |
| `UserSession` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `FindSession()`, `InvalidateSession()` |
| `AuthenticationToken` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `FindToken()`, `RevokeToken()` |

## Profile

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `ProfilePage` | [templates/profile.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/profile.html), [static/site.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/site.js) | View profile page; edit `username` and `contact_details`; `profileForm submit`; result display |
| `ProfileController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetProfile()`, `ValidateProfileInput()`, `UpdateProfile()` |
| `UserProfile` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetProfileDetails()`, `UpdateProfileDetails()`, `SaveProfile()` |
| `UserAccount` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetUserAccount()` |

## Change Password

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `ChangePasswordPage` | [templates/settings.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/settings.html), [static/site.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/site.js) | Inputs for `current_password`, `new_password`, `confirm_new_password`; `changePasswordForm submit`; result display |
| `PasswordController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidationCurrentPassword()`, `ValidateNewPassword()`, `UpdatePassword()` |
| `UserProfile` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetPasswordHash()`, `UpdatePasswordHash()` |
| `PasswordHistory` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `StorePasswordHistory()`, `GetPreviousPasswords()` |

## Forgot Password

| BCE Style Extension Class | File | Methods / Implementation |
|---|---|---|
| `ForgotPasswordPage` | [templates/auth.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/auth.html), [static/auth.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/auth.js) | `forgotForm submit`; `resetForm submit`; `sendResetCodeButton click` |
| `ForgotPasswordController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `RequestResetCode()`, `ValidationResetCode()`, `ResetPassword()` |
| `PasswordResetVerification` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GenerateCode()`, `StoreCode()`, `CheckCode()` |

## Delete Account

| BCE Style Extension Class | File | Methods / Implementation |
|---|---|---|
| `DeleteAccountPage` | [templates/settings.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/settings.html), [static/site.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/site.js) | Input for `current_password`; `deleteAccountForm submit` |
| `DeleteAccountController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidationCurrentPassword()`, `DeleteAccount()` |
