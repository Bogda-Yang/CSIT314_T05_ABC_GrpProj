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
| `RegisterPage` | `auth_page()` `routers/user.py:91`, `handleRegister()` `static/auth.js:204`, `handleSendCode()` `static/auth.js:263` |
| `AuthController` | `ValidateRegistrationInput()` `services/user_service.py:431`, `CheckEmail()` `services/user_service.py:452`, `SendVerificationEmail()` `services/user_service.py:457`, `VerifyEmailAddress()` `services/user_service.py:461`, `RequestVerificationCode()` `services/user_service.py:465`, `ValidationVerificationCode()` `services/user_service.py:473`, `CreateAccount()` `services/user_service.py:477` |
| `UserAccount` | `CreateUser()` `models/user.py:22`, `SaveUser()` `models/user.py:33`, `CheckEmail()` `models/user.py:41` |
| `EmailVerification` | `GenerateCode()` `services/user_service.py:352`, `StoreCode()` `services/user_service.py:356`, `CheckCode()` `services/user_service.py:377` |

## U2 Login

| BCE Class | Method definitions |
|---|---|
| `LoginPage` | `auth_page()` `routers/user.py:91`, `handleLogin()` `static/auth.js:177` |
| `AuthController` | `ValidateCredentials()` `services/user_service.py:508`, `CreateSession()` `services/user_service.py:515`, `Login()` `services/user_service.py:532` |
| `UserAccount` | `GetUserByEmail()` `models/user.py:37`, `CheckPassword()` `models/user.py:45` |
| `UserSession` | `CreateSession()` `models/user.py:238`, `StoreSession()` `models/user.py:249` |
| `AuthenticationToken` | `CreateToken()` `models/user.py:274`, `FindToken()` `models/user.py:285`, `RevokeToken()` `models/user.py:291` |

## U3 Logout

| BCE Class | Method definitions |
|---|---|
| `DashboardPage` | `logout()` `routers/user.py:110` |
| `SessionController` | `RequestLogout()` `services/user_service.py:540`, `Logout()` `services/user_service.py:544`, `TerminateSession()` `services/user_service.py:550`, `ClearAuthentication()` `services/user_service.py:566` |
| `UserSession` | `FindSession()` `models/user.py:253`, `InvalidateSession()` `models/user.py:259` |
| `AuthenticationToken` | `FindToken()` `models/user.py:285`, `RevokeToken()` `models/user.py:291` |

## U4 Update Profile

| BCE Class | Method definitions |
|---|---|
| `ProfilePage` | `profile_page()` `routers/user.py:35` |
| `ProfileController` | `ViewCurrentProfile()` `services/user_service.py:572`, `GetProfile()` `services/user_service.py:576`, `ValidateProfileInput()` `services/user_service.py:609`, `UpdateProfile()` `services/user_service.py:641`, `SaveProfileChanges()` `services/user_service.py:681` |
| `UserProfile` | `GetProfileDetails()` `models/user.py:92`, `UpdateProfileDetails()` `models/user.py:96`, `SaveProfile()` `models/user.py:133` |
| `UserAccount` | `GetUserAccount()` `models/user.py:50` |

## U5 Change Password

| BCE Class | Method definitions |
|---|---|
| `ChangePasswordPage` | `settings_page()` `routers/user.py:65` |
| `PasswordController` | `ValidationCurrentPassword()` `services/user_service.py:749`, `ValidateNewPassword()` `services/user_service.py:760`, `ValidatePasswordPolicy()` `services/user_service.py:788`, `SendPasswordChangeNotification()` `services/user_service.py:803`, `UpdatePassword()` `services/user_service.py:812` |
| `UserProfile` | `GetPasswordHash()` `models/user.py:188`, `UpdatePasswordHash()` `models/user.py:192` |
| `PasswordHistory` | `StorePasswordHistory()` `models/user.py:208`, `GetPreviousPasswords()` `models/user.py:219` |
