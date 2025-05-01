package com.healthai.api.controller;

import com.healthai.api.dto.HealthDataDTO;
import com.healthai.api.model.HealthData;
import com.healthai.api.model.User;
import com.healthai.api.service.HealthDataService;
import com.healthai.api.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/health")
public class HealthDataController {

    @Autowired
    private HealthDataService healthDataService;

    @Autowired
    private UserService userService;

    @PostMapping("/data")
    public ResponseEntity<?> saveHealthData(@Valid @RequestBody HealthDataDTO healthDataDTO, Authentication authentication) {
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        User user = userService.findByEmail(userDetails.getUsername());
        
        HealthData healthData = healthDataService.saveHealthData(healthDataDTO, user);
        return new ResponseEntity<>(healthData, HttpStatus.CREATED);
    }

    @GetMapping("/data")
    public ResponseEntity<List<HealthData>> getHealthData(
            @RequestParam(required = false) String dataType,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate,
            Authentication authentication) {
        
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        User user = userService.findByEmail(userDetails.getUsername());
        
        LocalDate start = startDate != null ? LocalDate.parse(startDate) : null;
        LocalDate end = endDate != null ? LocalDate.parse(endDate) : null;
        
        List<HealthData> healthData = healthDataService.getUserHealthData(user.getId(), dataType, start, end);
        return ResponseEntity.ok(healthData);
    }

    @GetMapping("/data/{id}")
    public ResponseEntity<?> getHealthDataById(@PathVariable Long id, Authentication authentication) {
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        User user = userService.findByEmail(userDetails.getUsername());
        
        HealthData healthData = healthDataService.getHealthDataById(id);
        
        if (healthData == null) {
            return ResponseEntity.notFound().build();
        }
        
        if (!healthData.getUser().getId().equals(user.getId())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        
        return ResponseEntity.ok(healthData);
    }

    @PutMapping("/data/{id}")
    public ResponseEntity<?> updateHealthData(
            @PathVariable Long id,
            @Valid @RequestBody HealthDataDTO healthDataDTO,
            Authentication authentication) {
        
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        User user = userService.findByEmail(userDetails.getUsername());
        
        HealthData healthData = healthDataService.getHealthDataById(id);
        
        if (healthData == null) {
            return ResponseEntity.notFound().build();
        }
        
        if (!healthData.getUser().getId().equals(user.getId())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        
        HealthData updatedData = healthDataService.updateHealthData(id, healthDataDTO);
        return ResponseEntity.ok(updatedData);
    }

    @DeleteMapping("/data/{id}")
    public ResponseEntity<?> deleteHealthData(@PathVariable Long id, Authentication authentication) {
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        User user = userService.findByEmail(userDetails.getUsername());
        
        HealthData healthData = healthDataService.getHealthDataById(id);
        
        if (healthData == null) {
            return ResponseEntity.notFound().build();
        }
        
        if (!healthData.getUser().getId().equals(user.getId())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        
        healthDataService.deleteHealthData(id);
        return ResponseEntity.noContent().build();
    }
}
