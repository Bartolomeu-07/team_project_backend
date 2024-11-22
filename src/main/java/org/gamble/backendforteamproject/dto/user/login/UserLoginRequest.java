package org.gamble.backendforteamproject.dto.user.login;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotEmpty;

public record UserLoginRequest(
        @NotEmpty
        @Email
        String email,
        @NotEmpty
        String password
) { }
