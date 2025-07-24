using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using System.Collections;
using DG.Tweening;
using Api.Models;
using System.Linq;






public class NarrativeEventManager : MonoBehaviour
{
    [System.Serializable]
    private class StreamingMessageState
    {
        public string messageId;
        public string type;
        public string speakerId;
        public string title;
        public List<PlayerChoiceOptionModel> options;

        public string FullText = "";

        public bool IsFinal = false;

        public StreamingMessageState(string messageId, string type, string speakerId, string title, string content, List<PlayerChoiceOptionModel> options)
        {
            this.messageId = messageId;
            this.type = type;
            this.speakerId = speakerId;
            this.title = title;
            this.options = options != null
                ? new List<PlayerChoiceOptionModel>(options.Select(opt => new PlayerChoiceOptionModel
                {
                    label = opt.label,
                    type = opt.type
                }))
                : new List<PlayerChoiceOptionModel>();

            this.FullText = string.Copy(content ?? "");
        }

        public void AppendContent(string additional)
        {

            if (string.IsNullOrEmpty(additional)) return;


            FullText += additional;

        }

    }



    [SerializeField] private Image _opacityImage;
    [SerializeField] private Canvas _canvas;

    [SerializeField] private RectTransform _leftActiveParent;
    [SerializeField] private RectTransform _rightActiveParent;
    [SerializeField] private RectTransform _leftInactiveParent;
    [SerializeField] private RectTransform _rightInactiveParent;
    [SerializeField] private RectTransform _leftBackgroundParent;
    [SerializeField] private RectTransform _rightBackgroundParent;

    [SerializeField] private RectTransform _leftActiveCharacterAnchor;
    [SerializeField] private RectTransform _rightActiveCharacterAnchor;
    [SerializeField] private RectTransform _leftInactiveCharacterAnchor;
    [SerializeField] private RectTransform _rightInactiveCharacterAnchor;
    [SerializeField] private RectTransform _leftBackgroundCharacterAnchor;
    [SerializeField] private RectTransform _rightBackgroundCharacterAnchor;
    [SerializeField] private GameObject _talkingCharacterPrefab;

    [SerializeField] private Color _inactiveColor;
    [SerializeField] private Color _onBackgroundColor;

    [SerializeField] private RectTransform _textlogParent;
    [SerializeField] private GameObject _textlogThoughtPrefab;
    [SerializeField] private GameObject _textlogActionPrefab;
    [SerializeField] private GameObject _textlogDialoguePrefab;
    [SerializeField] private GameObject _textlogNarratorPrefab;

    private Dictionary<string, TalkingCharacter> _talkingCharacters;
    private Dictionary<string, TalkingCharacter> _leftTalkingCharacters;
    private Dictionary<string, TalkingCharacter> _rightTalkingCharacters;

    private TextlogManager _currentTextLog;

    [SerializeField] private PlayerChoiceHandler _choicesMenu;

    private List<StreamingMessageState> _messages = new List<StreamingMessageState>();
    private int _currentMessageIndex = 0;

    private bool _canExit = false;
    private string _currentSpeakerId = null;
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

    void Update()
    {
        // Detectamos cualquier click
        if (Input.GetMouseButtonDown(0))
        {
            OnUserClick();
        }
    }

    private void OnUserClick()
    {
        if (_messages.Count == 0) return;

        var current = _messages[_currentMessageIndex];
        // Solo reaccionamos cuando el mensaje actual ha terminado y está completamente mostrado
        if (!current.IsFinal || !_currentTextLog.HasShownAll())
            return;

        // Si estamos en el último mensaje…
        if (_currentMessageIndex == _messages.Count - 1)
        {
            // …y podemos salir, terminamos el evento
            if (_canExit)
                StartCoroutine(EndNarrativeEventCoroutine());
            // si no podemos salir (por ser choice), ignoramos el clic
        }
        else
        {
            // Hay un siguiente mensaje: lo mostramos
            AdvanceToNextMessage();
        }
    }



    public void SetUpNarrativeEvent(string eventId, List<string> characterIds)
    {
        _opacityImage.gameObject.SetActive(true);
        _canExit = false;
        StartCoroutine(FadeInOpacityBackground());
        SetUpTalkingCharacters(characterIds);
        SetUpInitialTextLog();
    }

    private void SetUpInitialTextLog()
    {
        GameObject textLogGO = Instantiate(_textlogThoughtPrefab, _textlogParent);
        RectTransform rect = textLogGO.GetComponent<RectTransform>();

        rect.localScale = new Vector3(0f, 1f, 1f);


        rect.DOScaleX(1f, 2f).SetEase(Ease.OutBack, 0.5f);


        _currentTextLog = textLogGO.GetComponent<TextlogManager>();
        _currentTextLog.Clear();
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
            GameObject playerGO = Instantiate(_talkingCharacterPrefab, _leftInactiveParent);
            TalkingCharacter playerCharacter = playerGO.GetComponent<TalkingCharacter>();
            CharacterData characterData = GameManager.Instance.GetCharacter(playerId);
            playerCharacter.Initialize(characterData);

            // Animación hacia anchor izquierdo
            InitialAnimateCharacterToAnchor(
                playerGO,
                _leftInactiveCharacterAnchor,
                fromRight: false,
                duration: 2f
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

            if (nextPlacingRight)
            {
                GameObject characterGO = rightUsed ? Instantiate(_talkingCharacterPrefab, _rightBackgroundParent) : Instantiate(_talkingCharacterPrefab, _rightInactiveParent);
                TalkingCharacter talkingCharacter = characterGO.GetComponent<TalkingCharacter>();
                CharacterData characterData = GameManager.Instance.GetCharacter(characterId);
                talkingCharacter.Initialize(characterData);

                _talkingCharacters[characterId] = talkingCharacter;

                RectTransform anchor = rightUsed ? _rightBackgroundCharacterAnchor : _rightInactiveCharacterAnchor;

                InitialAnimateCharacterToAnchor(
                    characterGO,
                    anchor,
                    fromRight: true,
                    duration: 2f
                );

                talkingCharacter.SetFlip(true); // Mirando a la izquierda
                _rightTalkingCharacters[characterId] = talkingCharacter;

                rightUsed = true;
            }
            else
            {
                GameObject characterGO = leftUsed ? Instantiate(_talkingCharacterPrefab, _leftBackgroundParent) : Instantiate(_talkingCharacterPrefab, _leftInactiveParent);
                TalkingCharacter talkingCharacter = characterGO.GetComponent<TalkingCharacter>();
                CharacterData characterData = GameManager.Instance.GetCharacter(characterId);
                talkingCharacter.Initialize(characterData);

                _talkingCharacters[characterId] = talkingCharacter;
                
                RectTransform anchor = leftUsed ? _leftBackgroundCharacterAnchor : _leftInactiveCharacterAnchor;

                InitialAnimateCharacterToAnchor(
                    characterGO,
                    anchor,
                    fromRight: false,
                    duration: 2f
                );

                talkingCharacter.SetFlip(false); // Mirando a la derecha
                _leftTalkingCharacters[characterId] = talkingCharacter;

                leftUsed = true;
            }

            nextPlacingRight = !nextPlacingRight;
        }
    }



    private void InitialAnimateCharacterToAnchor(GameObject characterGO, RectTransform targetAnchor, bool fromRight, float duration = 2f)
    {
        RectTransform rect = characterGO.GetComponent<RectTransform>();

        Vector2 screenStartPos = fromRight
            ? new Vector2(Screen.width + 300f, Screen.height / 2f)
            : new Vector2(-300f, Screen.height / 2f);

        // Convertimos esa posición de pantalla a posición mundial para el canvas
        Vector3 worldStartPos;
        RectTransformUtility.ScreenPointToWorldPointInRectangle(
            _canvas.GetComponent<RectTransform>(),
            screenStartPos,
            _canvas.worldCamera,
            out worldStartPos
        );

        rect.position = worldStartPos;
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
        float targetAlpha = 0.9f;

        while (time < duration)
        {
            time += Time.deltaTime;
            float alpha = Mathf.Lerp(startAlpha, targetAlpha, time / duration);
            _opacityImage.color = new Color(_opacityImage.color.r, _opacityImage.color.g, _opacityImage.color.b, alpha);
            yield return null;
        }
    }



    public void OnParsedMessageReceived(StreamedMessage message)
    {
        bool isFirstMessage = _messages.Count == 0;

        // 1) Encontrar o crear el estado
        var existing = _messages.FirstOrDefault(m => m.messageId == message.message_id);
        if (existing != null)
        {
            existing.AppendContent(message.content);
        }
        else
        {
            var newMsg = new StreamingMessageState(
                message.message_id,
                message.type,
                message.speaker_id,
                message.title,
                message.content,
                message.options
            );
            _messages.Add(newMsg);
            existing = newMsg;

            // Si era el primero, instanciamos aquí el TextLog del tipo adecuado
            if (isFirstMessage)
            {
                if (_currentTextLog != null)
                    Destroy(_currentTextLog.gameObject);
                GameObject prefab;

                if (message.type == "player_choice")
                {

                    // Mostramos las opciones con título y lista de opciones
                    _choicesMenu.ShowChoices(
                        message.title,
                        message.options,
                        choiceLabel =>
                        {
                            PrepareForResumeAfterChoice();
                        }
                    );
                    return;
                }

                switch (message.type)
                {
                    case "dialogue": prefab = _textlogDialoguePrefab; break;
                    case "action": prefab = _textlogActionPrefab; break;
                    case "thought": prefab = _textlogThoughtPrefab; break;
                    case "narrator": prefab = _textlogNarratorPrefab; break;
                    default: prefab = _textlogDialoguePrefab; break;
                }

                var go = Instantiate(prefab, _textlogParent);
                var rect = go.GetComponent<RectTransform>();

                _currentTextLog = go.GetComponent<TextlogManager>();
                _currentTextLog.Clear();

                string speakerName = _talkingCharacters.ContainsKey(message.speaker_id)
                    ? _talkingCharacters[message.speaker_id].CharacterData.fullName
                    : "";
                bool onLeft = _leftTalkingCharacters.ContainsKey(message.speaker_id);

                _currentTextLog.UpdateLeftName(onLeft ? speakerName : "", onLeft);
                _currentTextLog.UpdateRightName(!onLeft ? speakerName : "", !onLeft);
                UpdateCharacterStates(_currentSpeakerId);
                _currentSpeakerId = message.speaker_id;
            }
        }

        // 2) Marcar como final todos los mensajes **anteriores** al que acaba de llegar
        int newIndex = _messages.IndexOf(existing);
        for (int i = 0; i < newIndex; i++)
        {
            _messages[i].IsFinal = true;
        }

        // 3) Si este mensaje es el que estamos mostrando, lo escribimos en el textlog
        if (newIndex == _currentMessageIndex)
        {
            _currentTextLog.AppendText(message.content);
        }

        // 4) Si el mensaje actual ha terminado y ya se ha mostrado todo, habilita avanzar
        var current = _messages[_currentMessageIndex];
        if (current.IsFinal && _currentTextLog.HasShownAll())
        {
            // Aquí podrías, por ejemplo, mostrar un indicador para que el usuario haga click,
            // o bien avanzar automáticamente:
            // AdvanceToNextMessage();
        }
    }

    private void AdvanceToNextMessage()
    {
        if (_messages[_currentMessageIndex].type == "player_choice")
            return;

        // destruye el TextLog viejo
        if (_currentTextLog != null)
            Destroy(_currentTextLog.gameObject);


        _currentMessageIndex++;

        var next = _messages[_currentMessageIndex];
        UpdateCharacterStates(next.speakerId);
        // flujo special para choice
        if (next.type == "player_choice")
        {
            _choicesMenu.ShowChoices(next.title, next.options, choiceLabel =>
                NarrativeStreamerAPI.Instance.SendPlayerChoice(choiceLabel)
            );
            return;
        }

        // instanciar prefab según tipo
        GameObject prefab = next.type switch
        {
            "dialogue" => _textlogDialoguePrefab,
            "action" => _textlogActionPrefab,
            "thought" => _textlogThoughtPrefab,
            "narrator" => _textlogNarratorPrefab,
            _ => _textlogDialoguePrefab
        };

        var go = Instantiate(prefab, _textlogParent);
        var rect = go.GetComponent<RectTransform>();
        rect.localScale = new Vector3(0f, 1f, 1f);
        rect.DOScaleX(1f, 0.5f).SetEase(Ease.OutBack);

        _currentTextLog = go.GetComponent<TextlogManager>();
        _currentTextLog.Clear();

        // nombre del hablante
        string speakerName = _talkingCharacters.GetValueOrDefault(next.speakerId)?.CharacterData.fullName ?? "";
        bool onLeft = _leftTalkingCharacters.ContainsKey(next.speakerId);
        _currentTextLog.UpdateLeftName(onLeft ? speakerName : "", onLeft);
        _currentTextLog.UpdateRightName(!onLeft ? speakerName : "", !onLeft);

        // y rellenamos con lo recibido hasta ahora
        _currentTextLog.AppendText(next.FullText);
    }

    private IEnumerator EndNarrativeEventCoroutine()
    {
        // tu fade-out y limpieza…
        float duration = 1f, t = 0f;
        var orig = _opacityImage.color;
        while (t < duration)
        {
            t += Time.deltaTime;
            _opacityImage.color = new Color(orig.r, orig.g, orig.b, Mathf.Lerp(orig.a, 0f, t / duration));
            yield return null;
        }
        _opacityImage.color = new Color(orig.r, orig.g, orig.b, 0f);
        _opacityImage.gameObject.SetActive(false);

        if (_currentTextLog != null) Destroy(_currentTextLog.gameObject);
        _messages.Clear();
        _currentMessageIndex = 0;
        _canExit = false;

        foreach (var kv in _talkingCharacters.Values)
            if (kv != null) Destroy(kv.gameObject);
        _talkingCharacters.Clear();
        _leftTalkingCharacters.Clear();
        _rightTalkingCharacters.Clear();

        Debug.Log("[NarrativeEventManager] Event finished and cleaned up.");
    }

    public void OnStreamCompleted()
    {
        // decides if the last message lets you exit
        if (_messages.Count == 0)
        {
            _canExit = false;
            Debug.LogWarning("[NarrativeEventManager] Stream completed but no messages were received.");
            return;
        }

        // Decide if we can exit depending on the last message type
        _canExit = _messages.Last().type != "player_choice";

        _messages[_messages.Count - 1].IsFinal = true;

        Debug.Log($"[NarrativeEventManager] canExit = {_canExit}");
    }

    public void PrepareForResumeAfterChoice()
    {
        // 1) Oculta el menú de opciones si aún sigue visible
        _choicesMenu.gameObject.SetActive(false);

        // 2) Destruye el TextLog antiguo
        if (_currentTextLog != null)
        {
            Destroy(_currentTextLog.gameObject);
            _currentTextLog = null;
        }

        // 3) Limpia mensajes y resetea índice
        _messages.Clear();
        _currentMessageIndex = 0;

        // 4) (Opcional) resetear canExit si usas esa lógica
        _canExit = false;
    }


    private void UpdateCharacterStates(string newSpeakerId)
    {
        if (newSpeakerId == _currentSpeakerId)
            return;

        // 1) Sacar al viejo speaker
        if (_currentSpeakerId != null && _talkingCharacters.TryGetValue(_currentSpeakerId, out var oldChar))
        {
            bool wasLeft = _leftTalkingCharacters.ContainsKey(_currentSpeakerId);
            bool sameSide = wasLeft == _leftTalkingCharacters.ContainsKey(newSpeakerId);

            // Definimos padre, ancla y color objetivo
            (RectTransform parent, RectTransform anchor, Color col) = wasLeft
                ? (sameSide
                    ? (_leftBackgroundParent, _leftBackgroundCharacterAnchor, _onBackgroundColor)
                    : (_leftInactiveParent, _leftInactiveCharacterAnchor, _inactiveColor))
                : (sameSide
                    ? (_rightBackgroundParent, _rightBackgroundCharacterAnchor, _onBackgroundColor)
                    : (_rightInactiveParent, _rightInactiveCharacterAnchor, _inactiveColor));

            AnimateCharacterToAnchor(oldChar, parent, anchor, col, duration: 0.5f);
        }

        // 2) Llevar al nuevo speaker a active
        if (_talkingCharacters.TryGetValue(newSpeakerId, out var newChar))
        {
            bool isLeft = _leftTalkingCharacters.ContainsKey(newSpeakerId);
            var parent = isLeft ? _leftActiveParent : _rightActiveParent;
            var anchor = isLeft ? _leftActiveCharacterAnchor : _rightActiveCharacterAnchor;
            var colActive = Color.white;

            AnimateCharacterToAnchor(newChar, parent, anchor, colActive, duration: 0.5f);
        }

        _currentSpeakerId = newSpeakerId;
    }

    private void AnimateCharacterToAnchor(
        TalkingCharacter character,
        RectTransform containerParent,
        RectTransform anchor,
        Color targetColor,
        float duration = 0.5f
    )
    {
        var rect = character.GetComponent<RectTransform>();
        // Temporalmente fuera de cualquier layout para animar sin saltos
        rect.SetParent(_canvas.transform, worldPositionStays: true);

        // Creamos la secuencia: posición, escala y color
        DOTween.Sequence()
            .Append(rect.DOMove(anchor.position, duration).SetEase(Ease.OutBack))
            .Join(rect.DOScale(Vector3.one, duration).SetEase(Ease.OutBack))
            .Join(DOVirtual.Color(
                character.GetColor(),   // Getter, asume que TalkingCharacter tiene GetColor()
                targetColor,
                duration,
                c => character.SetColor(c)
            ))
            .OnComplete(() =>
            {
                // Finalmente lo parentamos en su contenedor
                rect.SetParent(containerParent, worldPositionStays: true);
            });
    }
}
