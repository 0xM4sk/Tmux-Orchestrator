"""
Data Processor Module

This module provides functionality for processing and transforming data.
It handles data transformation, aggregation, and analysis operations.
"""

from typing import Dict, List, Any, Optional, Callable, Union
import logging
from datetime import datetime
from threading import Lock
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class ProcessingPipeline:
    """Represents a data processing pipeline"""
    pipeline_id: str
    steps: List[Callable]
    enabled: bool = True
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().timestamp()


class DataProcessor:
    """
    Processes and transforms data for the system.
    
    This class handles data transformation, aggregation, and analysis operations.
    """
    
    def __init__(self):
        """Initialize the DataProcessor with empty pipeline storage."""
        self._pipelines: Dict[str, ProcessingPipeline] = {}
        self._transformers: Dict[str, Callable] = {}
        self._aggregators: Dict[str, Callable] = {}
        self._lock = Lock()
    
    def register_transformer(self, name: str, transformer: Callable) -> bool:
        """
        Register a data transformer function.
        
        Args:
            name (str): The name of the transformer
            transformer (Callable): The transformer function
            
        Returns:
            bool: True if transformer was registered successfully, False otherwise
        """
        self._transformers[name] = transformer
        logger.debug(f"Registered transformer: {name}")
        return True
    
    def unregister_transformer(self, name: str) -> bool:
        """
        Unregister a data transformer function.
        
        Args:
            name (str): The name of the transformer to unregister
            
        Returns:
            bool: True if transformer was unregistered successfully, False otherwise
        """
        if name in self._transformers:
            del self._transformers[name]
            logger.debug(f"Unregistered transformer: {name}")
            return True
        return False
    
    def register_aggregator(self, name: str, aggregator: Callable) -> bool:
        """
        Register a data aggregator function.
        
        Args:
            name (str): The name of the aggregator
            aggregator (Callable): The aggregator function
            
        Returns:
            bool: True if aggregator was registered successfully, False otherwise
        """
        self._aggregators[name] = aggregator
        logger.debug(f"Registered aggregator: {name}")
        return True
    
    def unregister_aggregator(self, name: str) -> bool:
        """
        Unregister a data aggregator function.
        
        Args:
            name (str): The name of the aggregator to unregister
            
        Returns:
            bool: True if aggregator was unregistered successfully, False otherwise
        """
        if name in self._aggregators:
            del self._aggregators[name]
            logger.debug(f"Unregistered aggregator: {name}")
            return True
        return False
    
    def create_pipeline(self, pipeline_id: str, steps: List[Union[str, Callable]]) -> bool:
        """
        Create a data processing pipeline.
        
        Args:
            pipeline_id (str): The unique identifier for the pipeline
            steps (List[Union[str, Callable]]): The processing steps (transformer names or functions)
            
        Returns:
            bool: True if pipeline was created successfully, False otherwise
        """
        with self._lock:
            if pipeline_id in self._pipelines:
                logger.warning(f"Pipeline {pipeline_id} already exists")
                return False
            
            # Convert transformer names to functions
            resolved_steps = []
            for step in steps:
                if isinstance(step, str):
                    if step in self._transformers:
                        resolved_steps.append(self._transformers[step])
                    else:
                        logger.error(f"Transformer {step} not found")
                        return False
                else:
                    resolved_steps.append(step)
            
            pipeline = ProcessingPipeline(
                pipeline_id=pipeline_id,
                steps=resolved_steps
            )
            
            self._pipelines[pipeline_id] = pipeline
            logger.debug(f"Created pipeline {pipeline_id} with {len(resolved_steps)} steps")
            return True
    
    def update_pipeline(self, pipeline_id: str, steps: List[Union[str, Callable]]) -> bool:
        """
        Update an existing pipeline.
        
        Args:
            pipeline_id (str): The ID of the pipeline to update
            steps (List[Union[str, Callable]]): The new processing steps
            
        Returns:
            bool: True if pipeline was updated successfully, False otherwise
        """
        with self._lock:
            if pipeline_id not in self._pipelines:
                logger.warning(f"Pipeline {pipeline_id} not found")
                return False
            
            # Convert transformer names to functions
            resolved_steps = []
            for step in steps:
                if isinstance(step, str):
                    if step in self._transformers:
                        resolved_steps.append(self._transformers[step])
                    else:
                        logger.error(f"Transformer {step} not found")
                        return False
                else:
                    resolved_steps.append(step)
            
            pipeline = self._pipelines[pipeline_id]
            pipeline.steps = resolved_steps
            pipeline.updated_at = datetime.now().timestamp()
            
            logger.debug(f"Updated pipeline {pipeline_id}")
            return True
    
    def delete_pipeline(self, pipeline_id: str) -> bool:
        """
        Delete a pipeline.
        
        Args:
            pipeline_id (str): The ID of the pipeline to delete
            
        Returns:
            bool: True if pipeline was deleted successfully, False otherwise
        """
        with self._lock:
            if pipeline_id in self._pipelines:
                del self._pipelines[pipeline_id]
                logger.debug(f"Deleted pipeline {pipeline_id}")
                return True
            return False
    
    def enable_pipeline(self, pipeline_id: str) -> bool:
        """
        Enable a pipeline.
        
        Args:
            pipeline_id (str): The ID of the pipeline to enable
            
        Returns:
            bool: True if pipeline was enabled successfully, False otherwise
        """
        with self._lock:
            if pipeline_id in self._pipelines:
                self._pipelines[pipeline_id].enabled = True
                logger.debug(f"Enabled pipeline {pipeline_id}")
                return True
            return False
    
    def disable_pipeline(self, pipeline_id: str) -> bool:
        """
        Disable a pipeline.
        
        Args:
            pipeline_id (str): The ID of the pipeline to disable
            
        Returns:
            bool: True if pipeline was disabled successfully, False otherwise
        """
        with self._lock:
            if pipeline_id in self._pipelines:
                self._pipelines[pipeline_id].enabled = False
                logger.debug(f"Disabled pipeline {pipeline_id}")
                return True
            return False
    
    def process_data(self, data: Any, pipeline_id: Optional[str] = None, 
                    transformers: Optional[List[Union[str, Callable]]] = None) -> Any:
        """
        Process data using a pipeline or specific transformers.
        
        Args:
            data (Any): The data to process
            pipeline_id (Optional[str]): The ID of the pipeline to use
            transformers (Optional[List[Union[str, Callable]]]): Specific transformers to apply
            
        Returns:
            Any: The processed data
        """
        if pipeline_id:
            return self._process_with_pipeline(data, pipeline_id)
        elif transformers:
            return self._process_with_transformers(data, transformers)
        else:
            logger.warning("No pipeline or transformers specified for data processing")
            return data
    
    def _process_with_pipeline(self, data: Any, pipeline_id: str) -> Any:
        """
        Process data using a specific pipeline.
        
        Args:
            data (Any): The data to process
            pipeline_id (str): The ID of the pipeline to use
            
        Returns:
            Any: The processed data
        """
        with self._lock:
            if pipeline_id not in self._pipelines:
                logger.error(f"Pipeline {pipeline_id} not found")
                return data
            
            pipeline = self._pipelines[pipeline_id]
            if not pipeline.enabled:
                logger.warning(f"Pipeline {pipeline_id} is disabled")
                return data
        
        # Apply each step in the pipeline
        processed_data = data
        for i, step in enumerate(pipeline.steps):
            try:
                processed_data = step(processed_data)
                logger.debug(f"Applied step {i+1} of pipeline {pipeline_id}")
            except Exception as e:
                logger.error(f"Error in step {i+1} of pipeline {pipeline_id}: {e}")
                # Depending on requirements, we might want to stop or continue
                # For now, we'll continue with the partially processed data
                break
        
        return processed_data
    
    def _process_with_transformers(self, data: Any, transformers: List[Union[str, Callable]]) -> Any:
        """
        Process data using specific transformers.
        
        Args:
            data (Any): The data to process
            transformers (List[Union[str, Callable]]): The transformers to apply
            
        Returns:
            Any: The processed data
        """
        processed_data = data
        
        # Convert transformer names to functions
        resolved_transformers = []
        for transformer in transformers:
            if isinstance(transformer, str):
                if transformer in self._transformers:
                    resolved_transformers.append(self._transformers[transformer])
                else:
                    logger.error(f"Transformer {transformer} not found")
                    return data
            else:
                resolved_transformers.append(transformer)
        
        # Apply each transformer
        for i, transformer in enumerate(resolved_transformers):
            try:
                processed_data = transformer(processed_data)
                logger.debug(f"Applied transformer {i+1}")
            except Exception as e:
                logger.error(f"Error in transformer {i+1}: {e}")
                break
        
        return processed_data
    
    def aggregate_data(self, data: List[Any], aggregator_name: str, **kwargs) -> Any:
        """
        Aggregate data using a specific aggregator.
        
        Args:
            data (List[Any]): The data to aggregate
            aggregator_name (str): The name of the aggregator to use
            **kwargs: Additional arguments for the aggregator
            
        Returns:
            Any: The aggregated data
        """
        if aggregator_name not in self._aggregators:
            logger.error(f"Aggregator {aggregator_name} not found")
            return data
        
        try:
            aggregator = self._aggregators[aggregator_name]
            result = aggregator(data, **kwargs)
            logger.debug(f"Aggregated data using {aggregator_name}")
            return result
        except Exception as e:
            logger.error(f"Error in aggregator {aggregator_name}: {e}")
            return data
    
    def get_pipeline(self, pipeline_id: str) -> Optional[ProcessingPipeline]:
        """
        Get a pipeline by its ID.
        
        Args:
            pipeline_id (str): The ID of the pipeline to retrieve
            
        Returns:
            ProcessingPipeline: The pipeline, or None if not found
        """
        return self._pipelines.get(pipeline_id)
    
    def list_pipelines(self) -> List[str]:
        """
        List all pipeline IDs.
        
        Returns:
            List[str]: A list of all pipeline IDs
        """
        with self._lock:
            return list(self._pipelines.keys())
    
    def get_processor_info(self) -> Dict[str, Any]:
        """
        Get information about the data processor.
        
        Returns:
            Dict[str, Any]: Information about the data processor
        """
        with self._lock:
            pipeline_count = len(self._pipelines)
            enabled_pipelines = len([p for p in self._pipelines.values() if p.enabled])
            transformer_count = len(self._transformers)
            aggregator_count = len(self._aggregators)
            
            # Get pipeline step counts
            pipeline_steps = {}
            for pipeline_id, pipeline in self._pipelines.items():
                pipeline_steps[pipeline_id] = len(pipeline.steps)
            
            return {
                "pipeline_count": pipeline_count,
                "enabled_pipelines": enabled_pipelines,
                "transformer_count": transformer_count,
                "aggregator_count": aggregator_count,
                "pipeline_steps": pipeline_steps
            }