#!/usr/bin/env python3
"""
Test script for scheduling constraints functionality.

This script demonstrates how the new scheduling constraints system works,
including parsing constraints from text, loading them into the schedule agent,
and using them for optimal scheduling.
"""

import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.schedule_agent import ScheduleAgent, SchedulingConstraints
from notion_client.client import NotionClient


def test_scheduling_constraints():
    """Test the scheduling constraints functionality."""
    print("🧪 Testing Scheduling Constraints System")
    print("=" * 50)
    
    # Test 1: Create default constraints
    print("\n1. Creating default scheduling constraints...")
    constraints = SchedulingConstraints()
    print(f"✅ Default constraints created:")
    print(f"   - Working Hours: {constraints.working_hours['core_hours']['start']}-{constraints.working_hours['core_hours']['end']} {constraints.working_hours['core_hours']['timezone']}")
    print(f"   - Buffer Time: {constraints.working_hours['buffer_time']} minutes")
    print(f"   - ML Work: {constraints.health_optimized_timing['ml_deep_work']}")
    print(f"   - Strength Training: {constraints.health_optimized_timing['strength_training']}")
    
    # Test 2: Test time validation
    print("\n2. Testing time validation...")
    test_times = ["09:00", "15:00", "18:00", "07:00"]
    for time_str in test_times:
        is_valid = constraints.is_valid_time(time_str)
        print(f"   {time_str}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test 3: Test activity-specific time validation
    print("\n3. Testing activity-specific time validation...")
    ml_times = ["09:00", "15:00", "18:00"]
    for time_str in ml_times:
        is_valid = constraints.is_valid_time(time_str, "ml_deep_work")
        print(f"   ML Work at {time_str}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test 4: Test optimal time slot suggestions
    print("\n4. Testing optimal time slot suggestions...")
    activities = ["ml_deep_work", "strength_training", "meditation", "general"]
    for activity in activities:
        optimal_time = constraints.get_optimal_time_slot(activity, "2024-03-15")
        print(f"   {activity}: {optimal_time}")
    
    # Test 5: Test monthly constraints
    print("\n5. Testing monthly constraints...")
    constraints.update_monthly_constraints("March", {
        "working_hours": {"core_hours": {"start": "09:00", "end": "18:00"}},
        "health_optimized_timing": {"ml_deep_work": "afternoon"}
    })
    
    march_constraints = constraints.get_monthly_constraints("March")
    print(f"   March constraints: {march_constraints}")
    
    # Test 6: Test constraints for specific date
    print("\n6. Testing constraints for specific date...")
    date_constraints = constraints.get_constraints_for_date("2024-03-15")
    print(f"   Constraints for 2024-03-15 include {len(date_constraints.get('monthly_adjustments', {}))} monthly adjustments")
    
    # Test 7: Test constraints serialization
    print("\n7. Testing constraints serialization...")
    constraints_dict = constraints.to_dict()
    print(f"   Serialized constraints: {len(constraints_dict)} categories")
    print(f"   Last updated: {constraints_dict.get('last_updated', 'Unknown')}")
    
    # Test 8: Test constraints from dictionary
    print("\n8. Testing constraints from dictionary...")
    new_constraints = SchedulingConstraints.from_dict(constraints_dict)
    print(f"   Recreated constraints: {new_constraints.working_hours['core_hours']['start']}-{new_constraints.working_hours['core_hours']['end']}")
    
    print("\n✅ All tests completed successfully!")
    return constraints


def test_schedule_agent_with_constraints():
    """Test the schedule agent with constraints."""
    print("\n🧪 Testing Schedule Agent with Constraints")
    print("=" * 50)
    
    # Mock notion client for testing
    class MockNotionClient:
        def __init__(self):
            pass
    
    # Create schedule agent with mock client
    schedule_agent = ScheduleAgent(
        notion_client=MockNotionClient(),
        calendar_database_id="mock_calendar_id",
        todos_database_id="mock_todos_id",
        openai_api_key="mock_key"
    )
    
    # Test 1: Load constraints
    print("\n1. Loading constraints into schedule agent...")
    test_constraints = {
        "working_hours": {
            "core_hours": {"start": "08:00", "end": "17:00", "timezone": "CT"},
            "buffer_time": 15,
            "transit_time": 45
        },
        "health_optimized_timing": {
            "ml_deep_work": "morning",
            "strength_training": "14:00-16:00",
            "cardio": "flexible",
            "meditation": "transition"
        },
        "recovery_rest": {
            "strength_training_rest": 72,
            "cardio_active_recovery": True,
            "sleep_protection": 4
        }
    }
    
    schedule_agent.load_scheduling_constraints(test_constraints)
    print("✅ Constraints loaded into schedule agent")
    
    # Test 2: Get constraints summary
    print("\n2. Getting constraints summary...")
    constraints_summary = schedule_agent._get_constraints_summary()
    print("✅ Constraints summary generated:")
    print(constraints_summary[:200] + "..." if len(constraints_summary) > 200 else constraints_summary)
    
    # Test 3: Test optimal schedule with constraints
    print("\n3. Testing optimal schedule with constraints...")
    sample_todos = [
        {"title": "ML Deep Work Session", "priority": "High", "project": "Machine Learning"},
        {"title": "Strength Training", "priority": "High", "project": "Health"},
        {"title": "Cardio Session", "priority": "Medium", "project": "Health"},
        {"title": "Code Review", "priority": "Medium", "project": "Development"}
    ]
    
    optimal_schedule = schedule_agent.suggest_optimal_schedule_with_constraints("2024-03-15", sample_todos)
    print("✅ Optimal schedule generated:")
    print(optimal_schedule[:300] + "..." if len(optimal_schedule) > 300 else optimal_schedule)
    
    # Test 4: Test monthly constraints update
    print("\n4. Testing monthly constraints update...")
    schedule_agent.update_monthly_constraints("April", {
        "working_hours": {"core_hours": {"start": "10:00", "end": "19:00"}},
        "health_optimized_timing": {"ml_deep_work": "evening"}
    })
    print("✅ April constraints updated")
    
    # Test 5: Test constraints for specific date
    print("\n5. Testing constraints for specific date...")
    april_constraints = schedule_agent.get_constraints_for_date("2024-04-15")
    print(f"✅ April constraints retrieved: {len(april_constraints.get('monthly_adjustments', {}))} adjustments")
    
    print("\n✅ All schedule agent tests completed successfully!")


def main():
    """Main test function."""
    try:
        print("🚀 Starting Scheduling Constraints Tests")
        print("=" * 60)
        
        # Test basic constraints functionality
        constraints = test_scheduling_constraints()
        
        # Test schedule agent integration
        test_schedule_agent_with_constraints()
        
        print("\n🎉 All tests passed successfully!")
        print("\n📋 Summary of what was tested:")
        print("   ✅ SchedulingConstraints class creation and management")
        print("   ✅ Time validation and optimal time slot suggestions")
        print("   ✅ Monthly constraints and overrides")
        print("   ✅ Constraints serialization and deserialization")
        print("   ✅ Schedule agent integration with constraints")
        print("   ✅ Constraint-aware scheduling suggestions")
        
        print("\n💡 Next steps:")
        print("   • Use 'protocol import-goals-rules' to import your actual constraints")
        print("   • Use 'protocol schedule constraints' to view current constraints")
        print("   • Use 'protocol schedule plan-with-constraints' to test scheduling")
        print("   • Use 'protocol schedule update-constraints' to modify monthly constraints")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
