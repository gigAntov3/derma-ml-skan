export const initialModels = [
    {
      id: 1,
      name: "ResNet50 Skin Classifier",
      architecture: "resnet50",
      is_active: true,
      current_version: {
        id: 1,
        version: "1.2.0",
        file_name: "resnet50_skin_v1.2.0.pt",
        file_size: 98304000,
        created_at: "2024-01-15T10:30:00Z"
      },
      all_versions: [
        {
          id: 1,
          version: "1.2.0",
          file_name: "resnet50_skin_v1.2.0.pt",
          file_size: 98304000,
          created_at: "2024-01-15T10:30:00Z"
        },
        {
          id: 2,
          version: "1.1.0",
          file_name: "resnet50_skin_v1.1.0.pt",
          file_size: 95600000,
          created_at: "2023-12-10T14:20:00Z"
        }
      ],
      created_at: "2023-12-10T14:20:00Z",
      updated_at: "2024-01-15T10:30:00Z"
    },
    {
      id: 2,
      name: "EfficientNet-B3 Melanoma",
      architecture: "efficientnet_b3",
      is_active: false,
      current_version: {
        id: 3,
        version: "2.0.0",
        file_name: "efficientnet_melanoma_v2.0.0.pt",
        file_size: 156000000,
        created_at: "2024-02-01T09:15:00Z"
      },
      all_versions: [
        {
          id: 3,
          version: "2.0.0",
          file_name: "efficientnet_melanoma_v2.0.0.pt",
          file_size: 156000000,
          created_at: "2024-02-01T09:15:00Z"
        }
      ],
      created_at: "2024-02-01T09:15:00Z",
      updated_at: "2024-02-01T09:15:00Z"
    },
    {
      id: 3,
      name: "DenseNet121 Dermatology",
      architecture: "densenet121",
      is_active: false,
      current_version: {
        id: 4,
        version: "1.0.0",
        file_name: "densenet_dermatology_v1.0.0.pt",
        file_size: 78900000,
        created_at: "2024-02-10T11:45:00Z"
      },
      all_versions: [
        {
          id: 4,
          version: "1.0.0",
          file_name: "densenet_dermatology_v1.0.0.pt",
          file_size: 78900000,
          created_at: "2024-02-10T11:45:00Z"
        }
      ],
      created_at: "2024-02-10T11:45:00Z",
      updated_at: "2024-02-10T11:45:00Z"
    }
  ]
  
  export const architectureOptions = [
    { value: "resnet50", label: "ResNet50", description: "Базовая архитектура для классификации" },
    { value: "efficientnet_b3", label: "EfficientNet-B3", description: "Высокая точность, оптимизированная" },
    { value: "densenet121", label: "DenseNet121", description: "Плотные связи, хорошая точность" }
  ]