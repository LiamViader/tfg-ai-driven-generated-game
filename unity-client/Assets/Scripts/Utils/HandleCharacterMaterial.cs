using UnityEngine;

public class HandleCharacterMaterial : MonoBehaviour
{
    private Material _characterMaterial;
    [SerializeField] private Material _baseMaterial;
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void SetMaterialToSprite(SpriteRenderer spriteRenderer)
    {
        spriteRenderer.material = Instantiate(_baseMaterial) as Material;
        _characterMaterial = spriteRenderer.material;
    }

    public void SetHoverStrength(float strength)
    {
        if (_characterMaterial != null)
        {
            _characterMaterial.SetFloat("_HoverStrength", strength);
        }
    }

}
