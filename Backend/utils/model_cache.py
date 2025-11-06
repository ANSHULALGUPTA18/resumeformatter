"""
Model Cache Manager - Pre-load and cache all ML models at startup
This ensures the first request is fast by loading models during server initialization
"""

import time
from typing import Optional

# Global flag to track if models are pre-warmed
_models_prewarmed = False


def prewarm_models():
    """
    Pre-load all ML models at server startup for instant first request
    Call this in app.py after imports
    """
    global _models_prewarmed
    
    if _models_prewarmed:
        print("✅ Models already pre-warmed")
        return
    
    print("\n" + "="*70)
    print("🔥 PRE-WARMING ML MODELS FOR INSTANT PERFORMANCE")
    print("="*70)
    
    total_start = time.time()
    
    # 1. Pre-warm optimized section mapper
    try:
        print("\n1️⃣  Pre-warming Optimized Section Mapper...")
        start = time.time()
        from utils.optimized_section_mapper import get_optimized_mapper
        mapper = get_optimized_mapper()
        print(f"   ✅ Section mapper ready in {time.time()-start:.2f}s")
    except Exception as e:
        print(f"   ⚠️  Failed to pre-warm section mapper: {e}")
    
    # 2. Pre-warm enhanced section classifier
    try:
        print("\n2️⃣  Pre-warming Enhanced Section Classifier...")
        start = time.time()
        from utils.enhanced_section_classifier import EnhancedSectionClassifier
        classifier = EnhancedSectionClassifier()
        print(f"   ✅ Section classifier ready in {time.time()-start:.2f}s")
    except Exception as e:
        print(f"   ⚠️  Failed to pre-warm classifier: {e}")
    
    # 3. Pre-warm intelligent resume parser
    try:
        print("\n3️⃣  Pre-warming Intelligent Resume Parser...")
        start = time.time()
        from utils.intelligent_resume_parser import IntelligentResumeParser
        parser = IntelligentResumeParser()
        print(f"   ✅ Resume parser ready in {time.time()-start:.2f}s")
    except Exception as e:
        print(f"   ⚠️  Failed to pre-warm parser: {e}")
    
    # 4. Pre-warm section detector
    try:
        print("\n4️⃣  Pre-warming Section Detector...")
        start = time.time()
        from utils.section_detector import SectionDetector
        detector = SectionDetector(use_ml=True)
        print(f"   ✅ Section detector ready in {time.time()-start:.2f}s")
    except Exception as e:
        print(f"   ⚠️  Failed to pre-warm detector: {e}")
    
    total_time = time.time() - total_start
    
    print("\n" + "="*70)
    print(f"🎉 ALL MODELS PRE-WARMED IN {total_time:.2f}s")
    print("⚡ FIRST REQUEST WILL BE INSTANT!")
    print("="*70 + "\n")
    
    _models_prewarmed = True


def get_model_status():
    """
    Get the status of all cached models
    Returns dict with model names and their loaded status
    """
    status = {}
    
    # Check optimized section mapper
    try:
        from utils.optimized_section_mapper import OptimizedSectionMapper
        status['optimized_mapper'] = OptimizedSectionMapper._model_loaded
    except:
        status['optimized_mapper'] = False
    
    # Check enhanced section classifier
    try:
        from utils.enhanced_section_classifier import EnhancedSectionClassifier
        status['section_classifier'] = EnhancedSectionClassifier._models_loaded
    except:
        status['section_classifier'] = False
    
    # Check intelligent resume parser
    try:
        from utils.intelligent_resume_parser import IntelligentResumeParser
        status['resume_parser'] = IntelligentResumeParser._models_loaded
    except:
        status['resume_parser'] = False
    
    # Check section detector
    try:
        from utils.section_detector import SectionDetector
        status['section_detector'] = hasattr(SectionDetector, '_cached_model')
    except:
        status['section_detector'] = False
    
    return status


def clear_model_cache():
    """
    Clear all cached models (useful for debugging or memory management)
    """
    global _models_prewarmed
    
    print("🧹 Clearing model cache...")
    
    try:
        from utils.optimized_section_mapper import OptimizedSectionMapper
        OptimizedSectionMapper._model = None
        OptimizedSectionMapper._model_loaded = False
        OptimizedSectionMapper._embeddings_cache.clear()
    except:
        pass
    
    try:
        from utils.enhanced_section_classifier import EnhancedSectionClassifier
        EnhancedSectionClassifier._sentence_model = None
        EnhancedSectionClassifier._zero_shot_classifier = None
        EnhancedSectionClassifier._models_loaded = False
    except:
        pass
    
    try:
        from utils.intelligent_resume_parser import IntelligentResumeParser
        IntelligentResumeParser._model = None
        IntelligentResumeParser._nlp = None
        IntelligentResumeParser._models_loaded = False
    except:
        pass
    
    try:
        from utils.section_detector import SectionDetector
        if hasattr(SectionDetector, '_cached_model'):
            delattr(SectionDetector, '_cached_model')
    except:
        pass
    
    _models_prewarmed = False
    print("✅ Model cache cleared")


if __name__ == "__main__":
    # Test pre-warming
    print("Testing model pre-warming...")
    prewarm_models()
    
    print("\nModel Status:")
    status = get_model_status()
    for model_name, loaded in status.items():
        status_icon = "✅" if loaded else "❌"
        print(f"  {status_icon} {model_name}: {'Loaded' if loaded else 'Not loaded'}")
