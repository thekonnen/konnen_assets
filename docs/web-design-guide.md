# Identidade Visual, Cores e Tipografia: Konnen

## 🤖 Instruções para o Agente

Você é um agente especializado em UI/UX e desenvolvimento front-end. Seu objetivo é criar páginas web e interfaces de usuário utilizando a identidade visual da marca "Konnen". Siga estritamente as diretrizes de cores, gradientes e tipografia detalhadas neste documento para garantir consistência visual.

---

## 🎨 Paleta de Cores Base

A identidade principal da Konnen baseia-se em uma transição suave entre tons frios (verdes e azuis) e quentes (dourado/bronze).

| Nome da Cor | HEX Code | Posição no Gradiente | Uso Sugerido em UI | 
| ----- | ----- | ----- | ----- | 
| **Verde Água** | `#4B9F82` | Início (Esquerda) | Sucesso, Ícones, Destaques suaves | 
| **Cerceta (Teal)** | `#2C7D90` | Transição 1 | Elementos secundários, bordas | 
| **Azul Médio** | `#25659B` | Centro | Cor Primária (Botões, Links, Headers) | 
| **Azul Ardósia** | `#4F6D7B` | Transição 2 | Fundos de seções secundárias, subtítulos | 
| **Dourado/Bronze** | `#A18445` | Fim (Direita) | Ações de conversão (CTA), Alertas, Destaques premium | 

## 🌈 O Gradiente Konnen

A marca registrada da Konnen é um gradiente linear horizontal contínuo.

**Regra de Aplicação do Gradiente:**

* **Uso Ideal:** Fundos de seções hero (cabeçalhos), banners de destaque, barras de navegação superiores ou elementos gráficos de fundo. Textos de destaque (Eyebrows, tags de atenção).
* **Não recomendado:** Textos pequenos de leitura longa, botões muito estreitos ou fundos de grandes blocos de texto (prejudica a acessibilidade).

**Código CSS Pronto para o Agente:**

```css
/* Gradiente Padrão Konnen */
.bg-konnen-gradient {
  background: linear-gradient(100deg, #146B72, #0F4E86 60%, #9C7A2E); /* Baseado no CSS atual de produção */
}

/* Alternativa usando a paleta exata da logo */
.bg-logo-gradient {
  background: linear-gradient(90deg, #4B9F82 0%, #2C7D90 25%, #25659B 50%, #4F6D7B 75%, #A18445 100%);
}

/* Gradiente para Textos (Text Clipping) */
.text-konnen-gradient {
  background: linear-gradient(100deg, #146B72, #0F4E86 60%, #9C7A2E);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: transparent;
}
```

---

## ✍️ Tipografia (Fontes)

A Konnen utiliza uma combinação de três fontes do Google Fonts para criar uma hierarquia visual clara, moderna e voltada para tecnologia (Dev/AI).

**1. Bricolage Grotesque (Display / Títulos)**
* **Uso:** Exclusivo para Títulos principais (`h1`, `h2`), chamadas de impacto (Hero sections) e elementos de grande destaque.
* **Pesos recomendados:** 700 (Bold), 800 (ExtraBold).
* **Estilo:** Traz personalidade e força para a marca.

**2. Public Sans (Corpo / Leitura)**
* **Uso:** Textos de parágrafos (`p`), subtítulos longos, descrições de produtos e texto geral da interface.
* **Pesos recomendados:** 400 (Regular), 500 (Medium), 600 (SemiBold).
* **Estilo:** Neutra, altamente legível e limpa, garantindo conforto na leitura.

**3. IBM Plex Mono (Detalhes / Técnica)**
* **Uso:** Elementos de UI específicos como Tags, Badges, Botões pequenos, "Eyebrows" (textos acima de títulos), navegação, toggles de idioma e rodapé.
* **Pesos recomendados:** 400 (Regular), 500 (Medium).
* **Estilo:** Dá um toque "Tech/Desenvolvedor" característico de ferramentas de software e IA. Geralmente usada com `text-transform: uppercase` e `letter-spacing` (ex: `0.08em` a `0.14em`).

**Link de Importação (Google Fonts):**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=Public+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
```

---

## 🏗️ Variáveis CSS Globais (Design Tokens)

Para manter a consistência, injete estas variáveis no `:root` do seu CSS. Elas englobam cores, gradientes e as famílias tipográficas oficiais.

```css
:root {
  /* Cores da Marca (Extraídas da Logo) */
  --color-konnen-green: #4B9F82;
  --color-konnen-teal: #2C7D90;
  --color-konnen-blue: #25659B;
  --color-konnen-slate: #4F6D7B;
  --color-konnen-gold: #A18445;

  /* Cores de Produção (Tema Claro) */
  --k-teal: #146B72;
  --k-blue: #0F4E86;
  --k-gold: #9C7A2E;
  --k-gradient: linear-gradient(100deg, var(--k-teal), var(--k-blue) 60%, var(--k-gold));
  
  --ground: #F6F8F7;  /* Fundo da página */
  --card: #FFFFFF;    /* Fundo de cards/containers */
  --ink: #142A2C;     /* Texto principal */
  --muted: #5B6E6D;   /* Texto secundário/pálido */
  --line: #DBE4E3;    /* Bordas e divisores */
  --accent: var(--k-teal);
  --accent-soft: #E1EEEC; /* Hover states macios */

  /* Tipografia */
  --display: "Bricolage Grotesque", "Segoe UI", sans-serif;
  --body: "Public Sans", "Segoe UI", sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, monospace;
}

/* Modo Escuro (Dark Mode) */
@media (prefers-color-scheme: dark) {
  :root {
    --k-teal: #4FC3B8;
    --k-blue: #5FA8E8;
    --k-gold: #E0BB5C;
    --ground: #0E1513;
    --card: #14201E;
    --ink: #E8EDEC;
    --muted: #93A6A3;
    --line: #253634;
    --accent-soft: #1A2E2B;
  }
}
```

---

## 📌 Regras de UI/UX para o Agente

1. **Acessibilidade (Contraste):**
   * Nunca use texto branco sobre a cor `#4B9F82` (Verde Água) se a fonte for fina.
   * Respeite as variáveis `--ink` para textos principais e `--muted` para textos de apoio, alternando automaticamente com o Dark Mode.

2. **Hierarquia Tipográfica:**
   * Aplique `--display` com peso alto (700+) e `letter-spacing` ligeiramente negativo (ex: `-0.02em`) em títulos grandes para um visual moderno.
   * Aplique `--mono` em letras minúsculas (small text) com espaçamento positivo (ex: `0.08em` a `0.14em`) e em maiúsculas (`uppercase`) para categorias, tags e crachás (badges).

3. **Equilíbrio Visual (Bordas e Fundos):**
   * Utilize `border-radius: 1rem` para cards grandes e `999px` (pílula) para botões e tags, mantendo a consistência amigável da interface.
   * Use o gradiente (`--k-gradient`) preferencialmente em botões primários (`.btn.primary`) ou em textos de grande destaque (`-webkit-background-clip: text`).

4. **Interações (Hover):**
   * Para botões primários com gradiente, aplique um filtro de brilho (`filter: brightness(1.08)`) no estado de `:hover`.
   * Para botões secundários ou links, utilize o fundo `--accent-soft` ao passar o mouse.