package com.healthai.api.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDate;

@Data
public class HealthDataDTO {
    
    @NotBlank(message = "Data type is required")
    private String dataType;
    
    @NotNull(message = "Date is required")
    private LocalDate date;
    
    @NotNull(message = "Value is required")
    private Double value;
    
    private String unit;
    
    private String metadata;
    
    private String source;
}
