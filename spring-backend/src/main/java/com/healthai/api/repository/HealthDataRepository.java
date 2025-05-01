package com.healthai.api.repository;

import com.healthai.api.model.HealthData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface HealthDataRepository extends JpaRepository<HealthData, Long> {
    List<HealthData> findByUserId(Long userId);
    
    List<HealthData> findByUserIdAndDataType(Long userId, String dataType);
    
    @Query("SELECT h FROM HealthData h WHERE h.user.id = :userId AND (:dataType IS NULL OR h.dataType = :dataType) AND h.date BETWEEN :startDate AND :endDate ORDER BY h.date DESC")
    List<HealthData> findByUserIdAndDataTypeAndDateBetween(Long userId, String dataType, LocalDate startDate, LocalDate endDate);
    
    @Query("SELECT h FROM HealthData h WHERE h.user.id = :userId AND (:dataType IS NULL OR h.dataType = :dataType) AND h.date >= :startDate ORDER BY h.date DESC")
    List<HealthData> findByUserIdAndDataTypeAndDateAfter(Long userId, String dataType, LocalDate startDate);
    
    @Query("SELECT h FROM HealthData h WHERE h.user.id = :userId AND (:dataType IS NULL OR h.dataType = :dataType) AND h.date <= :endDate ORDER BY h.date DESC")
    List<HealthData> findByUserIdAndDataTypeAndDateBefore(Long userId, String dataType, LocalDate endDate);
    
    @Query("SELECT AVG(h.value) FROM HealthData h WHERE h.user.id = :userId AND h.dataType = :dataType AND h.date BETWEEN :startDate AND :endDate")
    Double getAverageValueByUserIdAndDataTypeAndDateBetween(Long userId, String dataType, LocalDate startDate, LocalDate endDate);
}
