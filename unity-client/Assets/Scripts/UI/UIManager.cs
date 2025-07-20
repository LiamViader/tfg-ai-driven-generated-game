using UnityEngine;
using UnityEngine.UI;
using TMPro;
using Unity.Burst.CompilerServices;
using System.Collections.Generic;
using System;


public class UIManager : MonoBehaviour
{
    public static UIManager Instance { get; private set; }
    [SerializeField] private TMP_Text _playerNameText;
    [SerializeField] private TMP_Text _playerAliasText;
    [SerializeField] private TMP_Text _scenarioNameText;
    [SerializeField] private Image _playerImage;
    [SerializeField] private Image _backgroundImage;


    public event Action<string> OnCharacterOptionsUpdated;

    private Dictionary<string, CharacterContextualUI> _activeCharacterContextualUIs = new();

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }

    }

    public void CharacterOptionsUpdated(string characterId)
    {
        OnCharacterOptionsUpdated?.Invoke(characterId);
    }

    public void RegisterCharacterContextualUI(string characterId, CharacterContextualUI ui, SpriteRenderer characterSpriteRenderer)
    {
        _activeCharacterContextualUIs[characterId] = ui;
        CharacterData character = GameManager.Instance.GetCharacter(characterId);
        string name = "";
        string alias = "";
        if (character != null)
        {
            if (character.fullName != null) name = character.fullName;
            if (character.alias != null) alias = character.alias;

        }
        ui.Initialize(characterId, characterSpriteRenderer, name, alias); // Inicializa el UI del personaje con su ID
    }

    // Y desregistrarlos cuando se desactivan
    public void UnregisterCharacterContextualUI(string characterId)
    {
        _activeCharacterContextualUIs.Remove(characterId);
    }

    public void SetPlayerData(CharacterData player)
    {
        if (player != null)
        {
            if (_playerNameText != null)
            {
                string name = "";
                if (player.fullName != null)
                {
                    name = player.fullName;
                }
                string alias = "";
                if (player.alias != null)
                {
                    alias = player.alias;
                }
                _playerNameText.text = name;
                _playerAliasText.text = alias;
            }

        }

    }

    public void SetPlayerImage(Texture2D image)
    {
        if (_playerImage == null || image == null) return;

        Rect rect = new Rect(0, 0, image.width, image.height);
        Vector2 pivot = new Vector2(0.5f, 0.5f);
        float pixelsPerUnit = 150f; // Aquí defines los 150 pixels por unidad

        Sprite sprite = Sprite.Create(image, rect, pivot, pixelsPerUnit);

        _playerImage.sprite = sprite;
        _playerImage.preserveAspect = true;

        AspectRatioFitter fitter = _playerImage.GetComponent<AspectRatioFitter>();
        if (fitter != null)
        {
            float aspect = (float)image.width / image.height;
            fitter.aspectRatio = aspect;
        }
        Debug.Log("IMAGE SET");
    }

    public void SetPlayerBackgroundImage(Texture2D background)
    {
        if (_backgroundImage == null || background == null) return;

        Rect rect = new Rect(0, 0, background.width, background.height);
        Vector2 pivot = new Vector2(0.5f, 0.5f);
        Sprite sprite = Sprite.Create(background, rect, pivot);

        _backgroundImage.sprite = sprite;
        _backgroundImage.preserveAspect = true;
    }

    public void SetScenarioData(ScenarioData scenario)
    {
        _scenarioNameText.text = "";
        if (scenario.name != null) _scenarioNameText.text = scenario.name;
    }

}
