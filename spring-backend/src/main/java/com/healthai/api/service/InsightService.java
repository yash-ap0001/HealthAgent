package com.healthai.api.service;

import com.healthai.api.dto.InsightDTO;
import com.healthai.api.model.Insight;
import com.healthai.api.model.User;
import com.healthai.api.repository.InsightRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class InsightService {

    @Autowired
    private InsightRepository insightRepository;

    public Insight createInsight(InsightDTO insightDTO, User user) {
        Insight insight = new Insight();
        insight.setUser(user);
        insight.setCategory(insightDTO.getCategory());
        insight.setTitle(insightDTO.getTitle());
        insight.setDescription(insightDTO.getDescription());
        insight.setSeverity(insightDTO.getSeverity());
        insight.setIsActionable(insightDTO.getIsActionable());
        insight.setRecommendation(insightDTO.getRecommendation());
        
        return insightRepository.save(insight);
    }

    public List<Insight> getUserInsights(Long userId, String category) {
        if (category == null) {
            return insightRepository.findByUserId(userId);
        } else {
            return insightRepository.findByUserIdAndCategory(userId, category);
        }
    }

    public Insight getInsightById(Long id) {
        return insightRepository.findById(id).orElse(null);
    }

    public Insight updateInsight(Long id, InsightDTO insightDTO) {
        Insight insight = insightRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Insight not found with id: " + id));
        
        insight.setCategory(insightDTO.getCategory());
        insight.setTitle(insightDTO.getTitle());
        insight.setDescription(insightDTO.getDescription());
        insight.setSeverity(insightDTO.getSeverity());
        insight.setIsActionable(insightDTO.getIsActionable());
        insight.setRecommendation(insightDTO.getRecommendation());
        
        return insightRepository.save(insight);
    }

    public void deleteInsight(Long id) {
        insightRepository.deleteById(id);
    }

    public List<Insight> getLatestInsights(Long userId) {
        return insightRepository.findLatestInsightsByUserId(userId);
    }

    public List<Insight> getActionableInsights(Long userId) {
        return insightRepository.findActionableInsightsByUserId(userId);
    }
}
