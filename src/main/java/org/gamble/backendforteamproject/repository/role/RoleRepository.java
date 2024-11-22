package org.gamble.backendforteamproject.repository.role;

import java.util.Optional;
import org.gamble.backendforteamproject.model.classes.Role;
import org.gamble.backendforteamproject.model.enums.UserRole;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

@Repository
public interface RoleRepository extends JpaRepository<Role, Long>,
        JpaSpecificationExecutor<Role> {
    Optional<Role> findByRole(UserRole name);
}
