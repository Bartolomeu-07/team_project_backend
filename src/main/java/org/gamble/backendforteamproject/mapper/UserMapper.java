package org.gamble.backendforteamproject.mapper;

import org.gamble.backendforteamproject.config.MapperConfig;
import org.gamble.backendforteamproject.dto.user.UserDto;
import org.gamble.backendforteamproject.dto.user.login.UserLoginResponseDto;
import org.gamble.backendforteamproject.dto.user.register.UserRegisterRequest;
import org.gamble.backendforteamproject.dto.user.register.UserRegisterResponseDto;
import org.gamble.backendforteamproject.model.classes.User;
import org.mapstruct.Mapper;

@Mapper(config = MapperConfig.class)
public interface UserMapper {

    UserDto toDto(User user);

    UserRegisterResponseDto toRegisterResponseDto(User user);

    UserLoginResponseDto toLoginResponseDto(User user);

    User toUser(UserRegisterRequest userRegisterRequest);
}
