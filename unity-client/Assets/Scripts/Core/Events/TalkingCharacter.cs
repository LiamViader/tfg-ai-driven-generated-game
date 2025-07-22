using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;

public class TalkingCharacter : MonoBehaviour
{
    [SerializeField] private Image _characterImage;



    private CharacterData _characterData;

    public CharacterData CharacterData { get; private set; }

    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    public void Initialize(CharacterData data)
    {
        if (data == null)
        {
            Debug.Log("ERROR DATA NULL");
        }
        _characterData = data;
        if (data.portrait == null) return;

        Texture2D image = data.portrait;

        Rect rect = new Rect(0, 0, image.width, image.height);
        Vector2 pivot = new Vector2(0.5f, 0.5f);
        float pixelsPerUnit = 150f; // Aquí defines los 150 pixels por unidad

        Sprite sprite = Sprite.Create(image, rect, pivot, pixelsPerUnit);

        _characterImage.sprite = sprite;
        _characterImage.preserveAspect = true;

        AspectRatioFitter fitter = _characterImage.GetComponent<AspectRatioFitter>();
        if (fitter != null)
        {
            float aspect = (float)image.width / image.height;
            fitter.aspectRatio = aspect;
        }
        Debug.Log("IMAGE SET");
        CharacterData = _characterData;
    }

    public void SetFlip(bool flip)
    {
        Vector3 scale = _characterImage.transform.localScale;
        scale.x = flip ? -1f : 1f;
        _characterImage.transform.localScale = scale;
    }

    public void SetColor(Color color)
    {
        _characterImage.color = color;
    }


}
