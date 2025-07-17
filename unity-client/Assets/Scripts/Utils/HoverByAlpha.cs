using UnityEngine;

[RequireComponent(typeof(SpriteRenderer))]
public class HoverByAlpha : MonoBehaviour
{
    [SerializeField] private Material _materialToUse;
    [SerializeField] private float minStrength = 0.3f;
    [SerializeField] private float maxStrength = 1f;
    [SerializeField] private float alphaThreshold = 0.1f;

    private Material _material;
    private SpriteRenderer _sr;
    private Texture2D _texture;
    private Sprite _sprite;

    void Awake()
    {
        _sr = GetComponent<SpriteRenderer>();
        _sprite = _sr.sprite;
        _texture = _sprite.texture;

        _material = Instantiate(_materialToUse);
        _sr.material = _material;
    }

    void Update()
    {
        Vector3 mouseWorld = Camera.main.ScreenToWorldPoint(Input.mousePosition);

        if (!_sr.bounds.Contains(mouseWorld))
        {
            _material.SetFloat("_HoverStrength", 0f);
            return;
        }

        // Convertir coordenadas del mundo a coordenadas de textura
        Vector2 localPos = transform.InverseTransformPoint(mouseWorld);
        Vector2 pivot = _sprite.pivot;
        float ppu = _sprite.pixelsPerUnit;

        Vector2 texCoord = new Vector2(
            pivot.x + localPos.x * ppu,
            pivot.y + localPos.y * ppu
        );

        // Redondear y clamping
        int x = Mathf.Clamp(Mathf.RoundToInt(texCoord.x), 0, _texture.width - 1);
        int y = Mathf.Clamp(Mathf.RoundToInt(texCoord.y), 0, _texture.height - 1);

        Color pixel = _texture.GetPixel(x, y);

        if (pixel.a > alphaThreshold)
        {
            // Calcula distancia desde el centro del sprite para variar la intensidad
            float distance = localPos.magnitude;
            float maxDist = _sr.bounds.extents.magnitude;
            float t = Mathf.Clamp01(distance / maxDist);
            float strength = Mathf.Lerp(maxStrength, minStrength, t);
            _material.SetFloat("_HoverStrength", strength);
        }
        else
        {
            _material.SetFloat("_HoverStrength", 0f);
        }
    }
}
