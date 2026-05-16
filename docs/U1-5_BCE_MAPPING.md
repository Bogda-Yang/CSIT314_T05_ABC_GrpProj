# U1-5 BCE Mapping

This version maps BCE classes and methods to real implementation definition lines.

Scope:

- `U1 Register`
- `U2 Login`
- `U3 Logout`
- `U4 Update Profile`
- `U5 Change Password`

Notes:

- FastAPI route handler functions in `routers/user.py` are framework URL endpoints.
- The U1-U5 Boundary flow code is implemented under explicit BCE Boundary classes in `routers/user.py`.
- Control and Entity classes map to their real service/model classes.
- Line references point to actual `class` or `def` definition lines.

## U1 Register

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `RegisterPage` | `class RegisterPage` `routers/user.py:142` | `auth_page()` `routers/user.py:146`, `send_code()` `routers/user.py:167`, `register()` `routers/user.py:180` |
| `AuthController` | `class AuthController` `services/user_service.py:479` | `ValidateRegistrationInput()` `services/user_service.py:481`, `CheckEmail()` `services/user_service.py:502`, `SendVerificationEmail()` `services/user_service.py:507`, `VerifyEmailAddress()` `services/user_service.py:511`, `RequestVerificationCode()` `services/user_service.py:515`, `ValidationVerificationCode()` `services/user_service.py:528`, `CreateAccount()` `services/user_service.py:532`, `CreateSession()` `services/user_service.py:572` |
| `UserAccount` | `class UserAccount` `models/user.py:12` | `CreateUser()` `models/user.py:25`, `SaveUser()` `models/user.py:38`, `GetUserByEmail()` `models/user.py:42`, `CheckEmail()` `models/user.py:46`, `MarkLastLogin()` `models/user.py:98` |
| `UserProfile` | `class UserProfile` `models/user.py:146` | `SaveProfile()` `models/user.py:207`, `GetProfileDetails()` `models/user.py:160` |
| `UserSession` | `class UserSession` `models/user.py:312` | `CreateSession()` `models/user.py:321`, `StoreSession()` `models/user.py:332` |
| `AuthenticationToken` | `class AuthenticationToken` `models/user.py:355` | `CreateToken()` `models/user.py:366` |
| `UserActivityLog` | `class UserActivityLog` `models/user.py:398` | `RecordActivity()` `models/user.py:408` |
| `EmailVerification` | `class EmailVerification` `services/user_service.py:399` | `GenerateCode()` `services/user_service.py:401`, `StoreCode()` `services/user_service.py:405`, `CheckCode()` `services/user_service.py:426` |

## U2 Login

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `LoginPage` | `class LoginPage` `routers/user.py:201` | `auth_page()` `routers/user.py:205`, `login()` `routers/user.py:226` |
| `AuthController` | `class AuthController` `services/user_service.py:479` | `ValidateCredentials()` `services/user_service.py:563`, `CreateSession()` `services/user_service.py:572`, `Login()` `services/user_service.py:591` |
| `UserAccount` | `class UserAccount` `models/user.py:12` | `GetUserByEmail()` `models/user.py:42`, `CheckPassword()` `models/user.py:50`, `MarkLastLogin()` `models/user.py:98` |
| `UserProfile` | `class UserProfile` `models/user.py:146` | `GetProfileDetails()` `models/user.py:160` |
| `UserSession` | `class UserSession` `models/user.py:312` | `CreateSession()` `models/user.py:321`, `StoreSession()` `models/user.py:332` |
| `AuthenticationToken` | `class AuthenticationToken` `models/user.py:355` | `CreateToken()` `models/user.py:366` |
| `UserActivityLog` | `class UserActivityLog` `models/user.py:398` | `RecordActivity()` `models/user.py:408` |

## U3 Logout

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `DashboardPage` | `class DashboardPage` `routers/user.py:232` | `logout()` `routers/user.py:236` |
| `SessionController` | `class SessionController` `services/user_service.py:597` | `RequestLogout()` `services/user_service.py:599`, `Logout()` `services/user_service.py:603`, `TerminateSession()` `services/user_service.py:609`, `ClearAuthentication()` `services/user_service.py:625` |
| `UserSession` | `class UserSession` `models/user.py:312` | `FindSession()` `models/user.py:336`, `InvalidateSession()` `models/user.py:347` |
| `AuthenticationToken` | `class AuthenticationToken` `models/user.py:355` | `FindToken()` `models/user.py:377`, `RevokeToken()` `models/user.py:390` |

## U4 Update Profile

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `ProfilePage` | `class ProfilePage` `routers/user.py:242` | `profile_page()` `routers/user.py:246`, `update_profile()` `routers/user.py:278`, `upload_profile_avatar()` `routers/user.py:295` |
| `ProfileController` | `class ProfileController` `services/user_service.py:629` | `GetProfile()` `services/user_service.py:635`, `ValidateProfileInput()` `services/user_service.py:668`, `UpdateProfile()` `services/user_service.py:700`, `UpdateAvatar()` `services/user_service.py:754` |
| `UserProfile` | `class UserProfile` `models/user.py:146` | `GetProfileDetails()` `models/user.py:160`, `UpdateProfileDetails()` `models/user.py:170`, `SaveProfile()` `models/user.py:207`, `UpdateAvatarPath()` `models/user.py:231` |
| `UserAccount` | `class UserAccount` `models/user.py:12` | `GetUserAccount()` `models/user.py:55` |

## U5 Change Password

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `ChangePasswordPage` | `class ChangePasswordPage` `routers/user.py:304` | `settings_page()` `routers/user.py:308`, `change_password()` `routers/user.py:336` |
| `PasswordController` | `class PasswordController` `services/user_service.py:806` | `ValidationCurrentPassword()` `services/user_service.py:808`, `ValidateNewPassword()` `services/user_service.py:819`, `ValidatePasswordPolicy()` `services/user_service.py:847`, `SendPasswordChangeNotification()` `services/user_service.py:862`, `UpdatePassword()` `services/user_service.py:875` |
| `UserAccount` | `class UserAccount` `models/user.py:12` | `GetUserAccount()` `models/user.py:55`, `CheckPassword()` `models/user.py:50` |
| `UserProfile` | `class UserProfile` `models/user.py:146` | `UpdatePasswordHash()` `models/user.py:266` |
| `PasswordHistory` | `class PasswordHistory` `models/user.py:272` | `StorePasswordHistory()` `models/user.py:282`, `GetPreviousPasswords()` `models/user.py:293` |
