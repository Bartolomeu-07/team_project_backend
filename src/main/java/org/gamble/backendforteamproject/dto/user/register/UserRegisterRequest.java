package org.gamble.backendforteamproject.dto.user.register;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import org.gamble.backendforteamproject.annotation.FieldMatch;
import org.hibernate.validator.constraints.Length;

@Data
@FieldMatch(first = "password", second = "repeatPassword",
        message = "The password fields must match")
public class UserRegisterRequest {
    @NotBlank
    @Length(min = 1, max = 50)
    private String username;
    @NotBlank
    @Length(min = 1, max = 50)
    private String firstName;
    @NotBlank
    @Length(min = 1, max = 50)
    private String lastName;
    @NotBlank
    @Email
    private String email;
    @NotBlank
    private String password;
    @NotBlank
    private String confirmPassword;


}
