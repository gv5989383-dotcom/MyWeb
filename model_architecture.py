import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Dense, GRU, TimeDistributed, Flatten, Dropout, Input, GlobalAveragePooling2D

def get_hybrid_model(input_shape=(128, 128, 3), sequence_length=10, num_classes=3):
    """
    Creates a Hybrid CNN + GRU model for Deepfake detection.
    Spatial Backbone: ResNet50 (pre-trained on ImageNet)
    Temporal Module: GRU for sequence analysis
    """
    # 1. Spatial Feature Extractor (CNN)
    base_model = ResNet50(include_top=False, weights='imagenet', input_shape=input_shape)
    # Freeze initial layers to preserve ImageNet features
    for layer in base_model.layers[:100]:
        layer.trainable = False
        
    cnn_model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Flatten()
    ], name="spatial_backbone")

    # 2. Temporal Module (RNN)
    # Input shape for sequence: (sequence_length, height, width, channels)
    sequence_input = Input(shape=(sequence_length,) + input_shape, name="video_input")
    
    # Apply CNN to each frame in the sequence
    x = TimeDistributed(cnn_model)(sequence_input)
    
    # Recurrent layers for temporal consistency
    x = GRU(128, return_sequences=False, dropout=0.3)(x)
    x = Dense(64, activation='relu')(x)
    x = Dropout(0.5)(x)
    
    # 3. Classification Head
    # Classes: 0: Authentic, 1: AI-Generated, 2: Manipulated (Face-swapped)
    outputs = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=sequence_input, outputs=outputs, name="Hybrid_Deepfake_Detector")
    
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    return model

def get_image_model(input_shape=(128, 128, 3), num_classes=3):
    """
    Standard ResNet50 model for static image analysis.
    """
    base_model = ResNet50(include_top=False, weights='imagenet', input_shape=input_shape)
    
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    outputs = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=outputs, name="ResNet_Image_Detector")
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    return model

if __name__ == "__main__":
    # Print summaries for verification
    img_model = get_image_model()
    print("\n--- Image Model Summary ---")
    img_model.summary()
    
    vid_model = get_hybrid_model()
    print("\n--- Hybrid Video Model Summary ---")
    vid_model.summary()
