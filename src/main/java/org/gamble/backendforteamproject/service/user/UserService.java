package org.gamble.backendforteamproject.service.user;

import org.gamble.backendforteamproject.dto.user.register.UserRegisterRequest;
import org.gamble.backendforteamproject.dto.user.register.UserRegisterResponseDto;

public interface UserService {
    UserRegisterResponseDto register(UserRegisterRequest userRegisterRequest);
}
