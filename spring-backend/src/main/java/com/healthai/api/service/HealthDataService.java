package com.healthai.api.service;

import com.healthai.api.dto.HealthDataDTO;
import com.healthai.api.model.HealthData;
import com.healthai.api.model.User;
import com.healthai.api.repository.HealthDataRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
public class HealthDataService {

    @Autowired
    private HealthDataRepository healthDataRepository;

    public HealthData saveHealthData(HealthDataDTO healthDataDTO, User user) {
        HealthData healthData = new HealthData();
        healthData.setUser(user);
        healthData.setDataType(healthDataDTO.getDataType());
        healthData.setDate(healthDataDTO.getDate());
        healthData.setValue(healthDataDTO.getValue());
        healthData.setUnit(healthDataDTO.getUnit());
        healthData.setMetadata(healthDataDTO.getMetadata());
        healthData.setSource(healthDataDTO.getSource());
        
        return healthDataRepository.save(healthData);
    }

    public List<HealthData> getUserHealthData(Long userId, String dataType, LocalDate startDate, LocalDate endDate) {
        if (dataType == null) {
            if (startDate != null && endDate != null) {
                return healthDataRepository.findByUserIdAndDataTypeAndDateBetween(userId, null, startDate, endDate);
            } else if (startDate != null) {
                return healthDataRepository.findByUserIdAndDataTypeAndDateAfter(userId, null, startDate);
            } else if (endDate != null) {
                return healthDataRepository.findByUserIdAndDataTypeAndDateBefore(userId, null, endDate);
            } else {
                return healthDataRepository.findByUserId(userId);
            }
        } else {
            if (startDate != null && endDate != null) {
                return healthDataRepository.findByUserIdAndDataTypeAndDateBetween(userId, dataType, startDate, endDate);
            } else if (startDate != null) {
                return healthDataRepository.findByUserIdAndDataTypeAndDateAfter(userId, dataType, startDate);
            } else if (endDate != null) {
                return healthDataRepository.findByUserIdAndDataTypeAndDateBefore(userId, dataType, endDate);
            } else {
                return healthDataRepository.findByUserIdAndDataType(userId, dataType);
            }
        }
    }

    public HealthData getHealthDataById(Long id) {
        return healthDataRepository.findById(id).orElse(null);
    }

    public HealthData updateHealthData(Long id, HealthDataDTO healthDataDTO) {
        HealthData healthData = healthDataRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Health data not found with id: " + id));
        
        healthData.setDataType(healthDataDTO.getDataType());
        healthData.setDate(healthDataDTO.getDate());
        healthData.setValue(healthDataDTO.getValue());
        healthData.setUnit(healthDataDTO.getUnit());
        healthData.setMetadata(healthDataDTO.getMetadata());
        healthData.setSource(healthDataDTO.getSource());
        
        return healthDataRepository.save(healthData);
    }

    public void deleteHealthData(Long id) {
        healthDataRepository.deleteById(id);
    }

    public Double getAverageValue(Long userId, String dataType, LocalDate startDate, LocalDate endDate) {
        return healthDataRepository.getAverageValueByUserIdAndDataTypeAndDateBetween(userId, dataType, startDate, endDate);
    }
}
