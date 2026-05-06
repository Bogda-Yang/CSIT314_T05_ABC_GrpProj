# U1-5 BCE Mapping

This version lists only real method/function definition lines.

Scope:

- `U1 Register`
- `U2 Login`
- `U3 Logout`
- `U4 Update Profile`
- `U5 Change Password`

Notes:

- Only actual `def` or `function` definitions are listed.
- Conceptual BCE boundary actions such as `EnterUsername()` or `DisplayLoginResult()` are not repeated unless there is a real code definition for them.

## U1 Register

| BCE Class | Method definitions |
|---|---|
| `RegisterPage` | `auth_page()` `routers/user.py:98`, `handleRegister()` `static/auth.js:204`, `handleSendCode()` `static/auth.js:263` |
| `AuthController` | `ValidateRegistrationInput()` `services/user_service.py:461`, `CheckEmail()` `services/user_service.py:482`, `SendVerificationEmail()` `services/user_service.py:487`, `VerifyEmailAddress()` `services/user_service.py:491`, `RequestVerificationCode()` `services/user_service.py:495`, `ValidationVerificationCode()` `services/user_service.py:503`, `CreateAccount()` `services/user_service.py:507` |
| `UserAccount` | `CreateUser()` `models/user.py:25`, `SaveUser()` `models/user.py:38`, `CheckEmail()` `models/user.py:46` |
| `EmailVerification` | `GenerateCode()` `services/user_service.py:381`, `StoreCode()` `services/user_service.py:385`, `CheckCode()` `services/user_service.py:406` |

## U2 Login

| BCE Class | Method definitions |
|---|---|
| `LoginPage` | `auth_page()` `routers/user.py:98`, `handleLogin()` `static/auth.js:177` |
| `AuthController` | `ValidateCredentials()` `services/user_service.py:538`, `CreateSession()` `services/user_service.py:547`, `Login()` `services/user_service.py:566` |
| `UserAccount` | `GetUserByEmail()` `models/user.py:42`, `CheckPassword()` `models/user.py:50` |
| `UserSession` | `CreateSession()` `models/user.py:292`, `StoreSession()` `models/user.py:303` |
| `AuthenticationToken` | `CreateToken()` `models/user.py:328`, `FindToken()` `models/user.py:339`, `RevokeToken()` `models/user.py:345` |

## U3 Logout

| BCE Class | Method definitions |
|---|---|
| `DashboardPage` | `logout()` `routers/user.py:120` |
| `SessionController` | `RequestLogout()` `services/user_service.py:574`, `Logout()` `services/user_service.py:578`, `TerminateSession()` `services/user_service.py:584`, `ClearAuthentication()` `services/user_service.py:600` |
| `UserSession` | `FindSession()` `models/user.py:307`, `InvalidateSession()` `models/user.py:313` |
| `AuthenticationToken` | `FindToken()` `models/user.py:339`, `RevokeToken()` `models/user.py:345` |

## U4 Update Profile

| BCE Class | Method definitions |
|---|---|
| `ProfilePage` | `profile_page()` `routers/user.py:36` |
| `ProfileController` | `ViewCurrentProfile()` `services/user_service.py:606`, `GetProfile()` `services/user_service.py:610`, `ValidateProfileInput()` `services/user_service.py:643`, `UpdateProfile()` `services/user_service.py:675`, `SaveProfileChanges()` `services/user_service.py:715` |
| `UserProfile` | `GetProfileDetails()` `models/user.py:140`, `UpdateProfileDetails()` `models/user.py:150`, `SaveProfile()` `models/user.py:187` |
| `UserAccount` | `GetUserAccount()` `models/user.py:55` |

## U5 Change Password

| BCE Class | Method definitions |
|---|---|
| `ChangePasswordPage` | `settings_page()` `routers/user.py:69` |
| `PasswordController` | `ValidationCurrentPassword()` `services/user_service.py:783`, `ValidateNewPassword()` `services/user_service.py:794`, `ValidatePasswordPolicy()` `services/user_service.py:822`, `SendPasswordChangeNotification()` `services/user_service.py:837`, `UpdatePassword()` `services/user_service.py:846` |
| `UserProfile` | `GetPasswordHash()` `models/user.py:242`, `UpdatePasswordHash()` `models/user.py:246` |
| `PasswordHistory` | `StorePasswordHistory()` `models/user.py:262`, `GetPreviousPasswords()` `models/user.py:273` |
