import os
import warnings
import logging
import sys

def disable_warning_messages():
    """
    VAŽNO: Ova funkcija MORA biti pozvana PRE importa bilo koje biblioteke!
    """
    # 1. Environment varijable (pre importa TensorFlow)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    
    # 2. Python warnings
    warnings.filterwarnings('ignore')
    warnings.filterwarnings('ignore', category=FutureWarning)
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    
    # 3. Logging
    logging.getLogger('tensorflow').setLevel(logging.ERROR)
    logging.getLogger('transformers').setLevel(logging.ERROR)
    logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
    logging.getLogger('huggingface_hub').setLevel(logging.ERROR)
    logging.getLogger('protobuf').setLevel(logging.ERROR)
    
    # 4. Privremeno redirectuj stderr (za protobuf greške)
    import io
    sys.stderr = io.StringIO()