package com.healthai.api.controller;

import com.healthai.api.dto.InsightDTO;
import com.healthai.api.model.Insight;
import com.healthai.api.model.User;
import com.healthai.api.service.InsightService;
import com.healthai.api.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/api/insights")
public class InsightController {

    @Autowired
    private InsightService insightService;

    @Autowired
    private UserService userService;

    @PostMapping
    public ResponseEntity<?> createInsight(
            @Valid @RequestBody InsightDTO insightDTO,
            Authentication authentication) {
        
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        User user = userService.findByEmail(userDetails.getUsername());
        
        Insight insight = insightService.createInsight(insightDTO, user);
        return new ResponseEntity<>(insight, HttpStatus.CREATED);
    }

    @GetMapping
    public ResponseEntity<List<Insight>> getUserInsights(
            @RequestParam(required = false) String category,
            Authentication authentication) {
        
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        User user = userService.findByEmail(userDetails.getUsername());
        
        List<Insight> insights = insightService.getUserInsights(user.getId(), category);
        return ResponseEntity.ok(insights);
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getInsightById(@PathVariable Long id, Authentication authentication) {
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        User user = userService.findByEmail(userDetails.getUsername());
        
        Insight insight = insightService.getInsightById(id);
        
        if (insight == null) {
            return ResponseEntity.notFound().build();
        }
        
        if (!insight.getUser().getId().equals(user.getId())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        
        return ResponseEntity.ok(insight);
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateInsight(
            @PathVariable Long id,
            @Valid @RequestBody InsightDTO insightDTO,
            Authentication authentication) {
        
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        User user = userService.findByEmail(userDetails.getUsername());
        
        Insight insight = insightService.getInsightById(id);
        
        if (insight == null) {
            return ResponseEntity.notFound().build();
        }
        
        if (!insight.getUser().getId().equals(user.getId())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        
        Insight updatedInsight = insightService.updateInsight(id, insightDTO);
        return ResponseEntity.ok(updatedInsight);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteInsight(@PathVariable Long id, Authentication authentication) {
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        User user = userService.findByEmail(userDetails.getUsername());
        
        Insight insight = insightService.getInsightById(id);
        
        if (insight == null) {
            return ResponseEntity.notFound().build();
        }
        
        if (!insight.getUser().getId().equals(user.getId())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        
        insightService.deleteInsight(id);
        return ResponseEntity.noContent().build();
    }
}
