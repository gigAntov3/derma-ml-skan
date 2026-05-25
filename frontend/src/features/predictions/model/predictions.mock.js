export const initialPredictionsHistory = {
    total: 5,
    skip: 0,
    limit: 50,
    predictions: [
      {
        id: 1,
        pacient_id: 1,
        image_url: "https://images.unsplash.com/photo-1584515933487-779824d29309?w=150&h=150&fit=crop",
        heatmap_url: "https://images.unsplash.com/photo-1584515933487-779824d29309?w=150&h=150&fit=crop&sat=-100",
        model: {
          id: 1,
          name: "ResNet50 Skin Classifier",
          architecture: "resnet50",
          is_active: true,
          current_version: { version: "1.2.0" }
        },
        malignant: {
          detected: true,
          probability: 0.94
        },
        melanoma: {
          detected: true,
          probability: 0.87
        },
        diagnosis: {
          detected: "melanoma",
          probabilities: {
            melanoma: 0.87,
            nevus: 0.05,
            basal_cell_carcinoma: 0.06,
            actinic_keratosis: 0.02
          }
        },
        created_at: "2024-03-15T10:30:00Z"
      },
      {
        id: 2,
        pacient_id: 1,
        image_url: "https://images.unsplash.com/photo-1584515933487-779824d29309?w=150&h=150&fit=crop",
        heatmap_url: null,
        model: {
          id: 1,
          name: "ResNet50 Skin Classifier",
          architecture: "resnet50",
          is_active: true,
          current_version: { version: "1.2.0" }
        },
        malignant: {
          detected: false,
          probability: 0.12
        },
        melanoma: {
          detected: false,
          probability: 0.08
        },
        diagnosis: {
          detected: "nevus",
          probabilities: {
            melanoma: 0.08,
            nevus: 0.85,
            basal_cell_carcinoma: 0.05,
            actinic_keratosis: 0.02
          }
        },
        created_at: "2024-03-10T14:20:00Z"
      },
      {
        id: 3,
        pacient_id: 1,
        image_url: "https://images.unsplash.com/photo-1584515933487-779824d29309?w=150&h=150&fit=crop",
        heatmap_url: "https://images.unsplash.com/photo-1584515933487-779824d29309?w=150&h=150&fit=crop&sat=-100",
        model: {
          id: 2,
          name: "EfficientNet-B3 Melanoma",
          architecture: "efficientnet_b3",
          is_active: false,
          current_version: { version: "2.0.0" }
        },
        malignant: {
          detected: true,
          probability: 0.91
        },
        melanoma: {
          detected: false,
          probability: 0.45
        },
        diagnosis: {
          detected: "basal_cell_carcinoma",
          probabilities: {
            melanoma: 0.45,
            nevus: 0.10,
            basal_cell_carcinoma: 0.40,
            actinic_keratosis: 0.05
          }
        },
        created_at: "2024-03-01T09:15:00Z"
      },
      {
        id: 4,
        pacient_id: 1,
        image_url: "https://images.unsplash.com/photo-1584515933487-779824d29309?w=150&h=150&fit=crop",
        heatmap_url: null,
        model: {
          id: 1,
          name: "ResNet50 Skin Classifier",
          architecture: "resnet50",
          is_active: true,
          current_version: { version: "1.2.0" }
        },
        malignant: {
          detected: false,
          probability: 0.08
        },
        melanoma: {
          detected: false,
          probability: 0.03
        },
        diagnosis: {
          detected: "actinic_keratosis",
          probabilities: {
            melanoma: 0.03,
            nevus: 0.10,
            basal_cell_carcinoma: 0.12,
            actinic_keratosis: 0.75
          }
        },
        created_at: "2024-02-20T11:45:00Z"
      },
      {
        id: 5,
        pacient_id: 1,
        image_url: "https://images.unsplash.com/photo-1584515933487-779824d29309?w=150&h=150&fit=crop",
        heatmap_url: "https://images.unsplash.com/photo-1584515933487-779824d29309?w=150&h=150&fit=crop&sat=-100",
        model: {
          id: 1,
          name: "ResNet50 Skin Classifier",
          architecture: "resnet50",
          is_active: true,
          current_version: { version: "1.2.0" }
        },
        malignant: {
          detected: false,
          probability: 0.05
        },
        melanoma: {
          detected: false,
          probability: 0.02
        },
        diagnosis: {
          detected: "nevus",
          probabilities: {
            melanoma: 0.02,
            nevus: 0.92,
            basal_cell_carcinoma: 0.04,
            actinic_keratosis: 0.02
          }
        },
        created_at: "2024-02-15T08:30:00Z"
      }
    ]
  }