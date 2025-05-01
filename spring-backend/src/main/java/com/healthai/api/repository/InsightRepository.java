package com.healthai.api.repository;

import com.healthai.api.model.Insight;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface InsightRepository extends JpaRepository<Insight, Long> {
    List<Insight> findByUserId(Long userId);
    
    List<Insight> findByUserIdAndCategory(Long userId, String category);
    
    @Query("SELECT i FROM Insight i WHERE i.user.id = :userId ORDER BY i.createdAt DESC")
    List<Insight> findLatestInsightsByUserId(Long userId);
    
    @Query("SELECT i FROM Insight i WHERE i.user.id = :userId AND i.isActionable = true ORDER BY i.severity DESC, i.createdAt DESC")
    List<Insight> findActionableInsightsByUserId(Long userId);
}
