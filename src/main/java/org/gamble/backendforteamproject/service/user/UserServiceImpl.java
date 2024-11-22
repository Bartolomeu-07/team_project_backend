package org.gamble.backendforteamproject.service.user;

import java.util.Set;
import lombok.RequiredArgsConstructor;
import org.gamble.backendforteamproject.dto.user.register.UserRegisterRequest;
import org.gamble.backendforteamproject.dto.user.register.UserRegisterResponseDto;
import org.gamble.backendforteamproject.exception.RegistrationException;
import org.gamble.backendforteamproject.mapper.UserMapper;
import org.gamble.backendforteamproject.model.classes.Role;
import org.gamble.backendforteamproject.model.classes.User;
import org.gamble.backendforteamproject.model.enums.UserRole;
import org.gamble.backendforteamproject.repository.role.RoleRepository;
import org.gamble.backendforteamproject.repository.user.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    private static final UserRole USER_ROLE = UserRole.USER;
    private static final Role ROLE = new Role();
    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;

    @Override
    public UserRegisterResponseDto register(UserRegisterRequest userRegisterRequest) {
        checkIfUserExist(userRegisterRequest);
        User user = getUser(userRegisterRequest);
        return userMapper.toRegisterResponseDto(
                userRepository.save(user)
        );
    }

    private User getUser(UserRegisterRequest userRegisterRequest) {
        User user = new User();
        user.setUsername(userRegisterRequest.getUsername());
        user.setFirstName(userRegisterRequest.getFirstName());
        user.setLastName(userRegisterRequest.getLastName());
        user.setEmail(userRegisterRequest.getEmail());
        user.setPassword(
                passwordEncoder.encode(userRegisterRequest.getPassword())
        );
        Role userRole = setUserRole();
        user.setRoles(Set.of(userRole));
        return user;
    }

    private Role setUserRole() {
        Role userRole = roleRepository.findByRole(USER_ROLE).orElseGet(
                () -> roleRepository.save(ROLE)
        );
        return userRole;
    }

    private void checkIfUserExist(UserRegisterRequest userRegisterRequest) {
        if (userRepository.findUserByEmail(userRegisterRequest.getEmail()).isPresent()) {
            throw new RegistrationException("Unable to complete registration");
        }
    }
}
