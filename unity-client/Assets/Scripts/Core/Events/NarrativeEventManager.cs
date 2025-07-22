using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using System.Collections;
using DG.Tweening;

public class NarrativeEventManager : MonoBehaviour
{
    [SerializeField] private Image _opacityImage;
    [SerializeField] private Canvas _canvas;

    [SerializeField] private RectTransform _leftActiveCharacterAnchor;
    [SerializeField] private RectTransform _rightActiveCharacterAnchor;
    [SerializeField] private RectTransform _leftInactiveCharacterAnchor;
    [SerializeField] private RectTransform _rightInactiveCharacterAnchor;
    [SerializeField] private RectTransform _leftBackgroundCharacterAnchor;
    [SerializeField] private RectTransform _rightBackgroundCharacterAnchor;
    [SerializeField] private GameObject _talkingCharacterPrefab;

    [SerializeField] private Color _inactiveColor;
    [SerializeField] private Color _onBackgroundColor;

    private Dictionary<string, TalkingCharacter> _talkingCharacters;
    private Dictionary<string, TalkingCharacter> _leftTalkingCharacters;
    private Dictionary<string, TalkingCharacter> _rightTalkingCharacters;

    public static NarrativeEventManager Instance { get; private set; }


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

    private void Start()
    {
        if (_canvas != null && Camera.main != null)
        {
            _canvas.worldCamera = Camera.main;
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    public void SetUpNarrativeEvent(string eventId, List<string> characterIds)
    {
        _opacityImage.gameObject.SetActive(true);
        StartCoroutine(FadeInOpacityBackground());
        SetUpTalkingCharacters(characterIds);
    }

    private void SetUpTalkingCharacters(List<string> characterIds)
    {
        _talkingCharacters = new Dictionary<string, TalkingCharacter>();
        _leftTalkingCharacters = new Dictionary<string, TalkingCharacter>();
        _rightTalkingCharacters = new Dictionary<string, TalkingCharacter>();

        bool leftUsed = false;
        bool rightUsed = false;
        bool nextPlacingRight = true;

        string playerId = GameManager.Instance.PlayerCharacterId;

        // 1. Si el jugador está en la lista, colócalo primero a la izquierda
        if (characterIds.Contains(playerId))
        {
            GameObject playerGO = Instantiate(_talkingCharacterPrefab, _canvas.transform);
            TalkingCharacter playerCharacter = playerGO.GetComponent<TalkingCharacter>();
            CharacterData characterData = GameManager.Instance.GetCharacter(playerId);
            playerCharacter.Initialize(characterData);

            // Animación hacia anchor izquierdo
            InitialAnimateCharacterToAnchor(
                playerGO,
                _leftInactiveCharacterAnchor,
                fromRight: false,
                duration: 1f
            );

            playerCharacter.SetFlip(false); // Mirando a la derecha

            _talkingCharacters[playerId] = playerCharacter;
            _leftTalkingCharacters[playerId] = playerCharacter;

            leftUsed = true;
        }

        // 2. Colocar el resto alternando derecha/izquierda
        foreach (string characterId in characterIds)
        {
            if (characterId == playerId)
                continue;

            GameObject characterGO = Instantiate(_talkingCharacterPrefab, _canvas.transform);
            TalkingCharacter talkingCharacter = characterGO.GetComponent<TalkingCharacter>();
            CharacterData characterData = GameManager.Instance.GetCharacter(characterId);
            talkingCharacter.Initialize(characterData);

            _talkingCharacters[characterId] = talkingCharacter;

            if (nextPlacingRight)
            {
                RectTransform anchor = rightUsed ? _rightBackgroundCharacterAnchor : _rightInactiveCharacterAnchor;

                InitialAnimateCharacterToAnchor(
                    characterGO,
                    anchor,
                    fromRight: true,
                    duration: 1f
                );

                talkingCharacter.SetFlip(true); // Mirando a la izquierda
                _rightTalkingCharacters[characterId] = talkingCharacter;

                rightUsed = true;
            }
            else
            {
                RectTransform anchor = leftUsed ? _leftBackgroundCharacterAnchor : _leftInactiveCharacterAnchor;

                InitialAnimateCharacterToAnchor(
                    characterGO,
                    anchor,
                    fromRight: false,
                    duration: 1f
                );

                talkingCharacter.SetFlip(false); // Mirando a la derecha
                _leftTalkingCharacters[characterId] = talkingCharacter;

                leftUsed = true;
            }

            nextPlacingRight = !nextPlacingRight;
        }
    }



    private void InitialAnimateCharacterToAnchor(GameObject characterGO, RectTransform targetAnchor, bool fromRight, float duration = 1f)
    {
        RectTransform rect = characterGO.GetComponent<RectTransform>();
        rect.SetParent(_canvas.transform, false); // libre movimiento temporal

        // Posición inicial fuera de pantalla
        Vector2 startPos = fromRight
            ? new Vector2(Screen.width + 300f, targetAnchor.position.y)
            : new Vector2(-300f, targetAnchor.position.y);

        rect.position = startPos;
        rect.localScale = Vector3.one * 0.6f; // arranca más pequeño

        // Creamos secuencia DOTween
        Sequence seq = DOTween.Sequence();

        // Movimiento
        seq.Join(rect.DOMove(targetAnchor.position, duration).SetEase(Ease.OutBack));
        // Escala
        seq.Join(rect.DOScale(Vector3.one, duration).SetEase(Ease.OutBack));

        // Al terminar, reparentamos y limpiamos
        seq.OnComplete(() =>
        {
            rect.SetParent(targetAnchor, false);
            rect.localPosition = Vector3.zero;
            rect.localScale = Vector3.one;
        });
    }

    Vector3 GetWorldScale(Transform t)
    {
        Vector3 scale = t.localScale;
        Transform parent = t.parent;
        while (parent != null)
        {
            scale = Vector3.Scale(scale, parent.localScale);
            parent = parent.parent;
        }
        return scale;
    }

    private IEnumerator FadeInOpacityBackground(float duration = 1f)
    {
        float time = 0f;
        float startAlpha = 0f;
        float targetAlpha = 0.8f;

        while (time < duration)
        {
            time += Time.deltaTime;
            float alpha = Mathf.Lerp(startAlpha, targetAlpha, time / duration);
            _opacityImage.color = new Color(_opacityImage.color.r, _opacityImage.color.g, _opacityImage.color.b, alpha);
            yield return null;
        }
    }
}
