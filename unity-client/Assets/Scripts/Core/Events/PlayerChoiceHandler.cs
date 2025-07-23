using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using Api.Models;

public class PlayerChoiceHandler : MonoBehaviour
{
    [Header("UI References")]
    [SerializeField] private RectTransform _choicesContainer;
    [SerializeField] private GameObject _choiceActionPrefab;
    [SerializeField] private GameObject _choiceDialoguePrefab;
    [SerializeField] private TMP_Text _choiceTitle;

    private Action<string> _onChoiceSelected;

    /// <summary>
    /// Muestra un conjunto de opciones al jugador.
    /// Usa distinto prefab según el tipo de cada opción.
    /// </summary>
    public void ShowChoices(string title, List<PlayerChoiceOptionModel> options, Action<string> onSelected)
    {
        // 1️⃣ Ponemos el título
        _choiceTitle.text = title;

        // 2️⃣ Limpiamos cualquier opción anterior
        foreach (Transform child in _choicesContainer)
            Destroy(child.gameObject);

        _onChoiceSelected = onSelected;

        // 3️⃣ Instanciamos un botón por cada opción, eligiendo prefab según tipo
        foreach (var opt in options)
        {
            GameObject prefab = opt.type == "Action"
                ? _choiceActionPrefab
                : _choiceDialoguePrefab;

            GameObject go = Instantiate(prefab, _choicesContainer);
            var btn = go.GetComponent<Button>();
            var label = go.GetComponentInChildren<TMP_Text>();

            label.text = opt.label;
            btn.onClick.AddListener(() => OnButtonClicked(opt.label));
        }

        // 4️⃣ Activamos el panel
        gameObject.SetActive(true);
    }

    private void OnButtonClicked(string label)
    {
        // Ocultamos el panel de opciones
        gameObject.SetActive(false);

        // Invocamos el callback con la etiqueta elegida
        _onChoiceSelected?.Invoke(label);
    }
}
