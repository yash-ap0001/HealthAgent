package com.healthai.api.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class InsightDTO {
    
    @NotBlank(message = "Category is required")
    private String category;
    
    @NotBlank(message = "Title is required")
    private String title;
    
    @NotBlank(message = "Description is required")
    private String description;
    
    @Min(1)
    @Max(5)
    private Integer severity;
    
    private Boolean isActionable;
    
    private String recommendation;
}
