using UnityEngine;

[ExecuteAlways]
[RequireComponent(typeof(Camera))]
public class FixedAspectCamera : MonoBehaviour
{
    [Header("Target aspect ratio")]
    [SerializeField] private Vector2 targetAspectRatio = new Vector2(16, 9);

    [Header("Scenario settings")]
    [SerializeField] private float scenarioHeightInPixels = 1440f;
    [SerializeField] private float pixelsPerUnit = 100;

    private Camera _camera;

    void Awake()
    {
        _camera = GetComponent<Camera>();
        UpdateViewport();
    }

#if UNITY_EDITOR
    void Update()
    {
        if (!Application.isPlaying)
            UpdateViewport();
    }
#endif

    void UpdateViewport()
    {
        if (_camera == null)
            _camera = GetComponent<Camera>();

        // 1. Calcular height del escenario en unidades
        float scenarioHeightInUnits = scenarioHeightInPixels / pixelsPerUnit;
        _camera.orthographicSize = scenarioHeightInUnits / 2f;

        // 2. Ajustar viewport con bandas negras (pillarbox / letterbox)
        float targetAspect = targetAspectRatio.x / targetAspectRatio.y;
        float windowAspect = (float)Screen.width / Screen.height;
        float scaleHeight = windowAspect / targetAspect;

        if (scaleHeight < 1f)
        {
            // Bandas horizontales
            Rect rect = new Rect(0f, (1f - scaleHeight) / 2f, 1f, scaleHeight);
            _camera.rect = rect;
        }
        else
        {
            // Bandas verticales
            float scaleWidth = 1f / scaleHeight;
            Rect rect = new Rect((1f - scaleWidth) / 2f, 0f, scaleWidth, 1f);
            _camera.rect = rect;
        }
    }
}
