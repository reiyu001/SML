import { useMemo, useState } from "react"

type TokenRow = {
  lexeme: string
  token: string
}

const sampleCode = `measure distance = 12.5 meter;
measure time = 2 second;

speed = distance / time;
print("Speed:", speed);`

const keywords = new Set([
  "break",
  "case",
  "const",
  "continue",
  "default",
  "else",
  "false",
  "for",
  "function",
  "if",
  "let",
  "measure",
  "null",
  "print",
  "return",
  "true",
  "var",
  "while",
])

const operators = new Set([
  "+",
  "-",
  "*",
  "/",
  "%",
  "=",
  "==",
  "===",
  "!=",
  "!==",
  "<",
  ">",
  "<=",
  ">=",
  "&&",
  "||",
  "!",
  "++",
  "--",
  "+=",
  "-=",
  "*=",
  "/=",
  "=>",
])

const punctuationNames: Record<string, string> = {
  "(": "LEFT_PAREN",
  ")": "RIGHT_PAREN",
  "{": "LEFT_BRACE",
  "}": "RIGHT_BRACE",
  "[": "LEFT_BRACKET",
  "]": "RIGHT_BRACKET",
  ",": "COMMA",
  ".": "DOT",
  ":": "COLON",
  ";": "SEMICOLON",
}

function tokenize(source: string): TokenRow[] {
  const matches =
    source.match(
      /\/\/[^\n]*|\/\*[\s\S]*?\*\/|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\d+(?:\.\d+)?|[A-Za-z_$][\w$]*|===|!==|==|!=|<=|>=|&&|\|\||\+\+|--|\+=|-=|\*=|\/=|=>|[+\-*/%=<>!]|[()[\]{},.:;]/g,
    ) ?? []

  return matches.map((lexeme) => {
    let token = "UNKNOWN"

    if (lexeme.startsWith("//") || lexeme.startsWith("/*")) token = "COMMENT"
    else if (/^["']/.test(lexeme)) token = "STRING_LITERAL"
    else if (/^\d/.test(lexeme))
      token = lexeme.includes(".") ? "DECIMAL_LITERAL" : "INTEGER_LITERAL"
    else if (keywords.has(lexeme)) token = `KEYWORD_${lexeme.toUpperCase()}`
    else if (/^[A-Za-z_$]/.test(lexeme)) token = "IDENTIFIER"
    else if (operators.has(lexeme)) token = "OPERATOR"
    else if (punctuationNames[lexeme]) token = punctuationNames[lexeme]

    return { lexeme, token }
  })
}

function CodeIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="m8.5 7-5 5 5 5M15.5 7l5 5-5 5M14 4l-4 16" />
    </svg>
  )
}

function SparkIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 3l1.2 4.3a5 5 0 0 0 3.5 3.5L21 12l-4.3 1.2a5 5 0 0 0-3.5 3.5L12 21l-1.2-4.3a5 5 0 0 0-3.5-3.5L3 12l4.3-1.2a5 5 0 0 0 3.5-3.5L12 3Z" />
    </svg>
  )
}

export default function App() {
  const [code, setCode] = useState(sampleCode)
  const [rows, setRows] = useState<TokenRow[]>([])
  const [hasAnalyzed, setHasAnalyzed] = useState(false)
  const lineCount = useMemo(() => code.split("\n").length, [code])

  const analyze = () => {
    setRows(tokenize(code))
    setHasAnalyzed(true)
  }

  const clear = () => {
    setCode("")
    setRows([])
    setHasAnalyzed(false)
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <CodeIcon />
          </div>
          <div>
            <h1>Standard Measurement Langugage</h1>
            <p>Lexical analysis workspace</p>
          </div>
        </div>
        <div className="status">
          <span />
          Analyzer ready
        </div>
      </header>

      <section className="intro">
        <div>
          <span className="eyebrow">Compiler toolkit</span>
          <h2>
            Understand your source,
            <br />
            one token at a time.
          </h2>
        </div>
        <p>
          Enter your programming language syntax and run the analyzer to
          identify every lexeme and its corresponding token.
        </p>
      </section>

      <section className="workspace">
        <article className="panel results-panel">
          <div className="panel-header">
            <div>
              <span className="panel-number">01</span>
              <div>
                <h3>Lexical output</h3>
                <p>Recognized source elements</p>
              </div>
            </div>
            <span className="count-badge">{rows.length} tokens</span>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>
                    <span>Lexemes</span>
                  </th>
                  <th>
                    <span>Tokens</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, index) => (
                  <tr key={`${row.lexeme}-${index}`}>
                    <td>
                      <span className="row-number">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <code>{row.lexeme}</code>
                    </td>
                    <td>
                      <span className="token-pill">{row.token}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {rows.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">
                  <SparkIcon />
                </div>
                <h4>{hasAnalyzed ? "No tokens found" : "Ready to analyze"}</h4>
                <p>
                  {hasAnalyzed
                    ? "Add valid source code and try again."
                    : "Your lexemes and tokens will appear here after analysis."}
                </p>
              </div>
            )}
          </div>
        </article>

        <article className="panel editor-panel">
          <div className="panel-header editor-heading">
            <div>
              <span className="panel-number">02</span>
              <div>
                <h3>Source language</h3>
                <p>Write or paste code to inspect</p>
              </div>
            </div>
            <button
              className="text-button"
              type="button"
              onClick={() => setCode(sampleCode)}
            >
              Load sample
            </button>
          </div>

          <div className="editor">
            <div className="editor-bar">
              <div className="window-dots">
                <i />
                <i />
                <i />
              </div>
              <span>main.sml</span>
              <span className="language-label">SML</span>
            </div>
            <div className="editor-body">
              <div className="line-numbers" aria-hidden="true">
                {Array.from({ length: lineCount }, (_, index) => (
                  <span key={index}>{index + 1}</span>
                ))}
              </div>
              <textarea
                aria-label="Source code"
                value={code}
                onChange={(event) => setCode(event.target.value)}
                onKeyDown={(event) => {
                  if ((event.ctrlKey || event.metaKey) && event.key === "Enter")
                    analyze()
                }}
                placeholder="// Enter your programming language here..."
                spellCheck={false}
              />
            </div>
            <div className="editor-footer">
              <span>
                {lineCount} {lineCount === 1 ? "line" : "lines"}
              </span>
              <span>{code.length} characters</span>
            </div>
          </div>

          <div className="actions">
            <button className="clear-button" type="button" onClick={clear}>
              Clear
            </button>
            <span className="shortcut">Ctrl + Enter</span>
            <button className="analyze-button" type="button" onClick={analyze}>
              Analyze language
              <svg viewBox="0 0 20 20" aria-hidden="true">
                <path d="M4 10h12m-5-5 5 5-5 5" />
              </svg>
            </button>
          </div>
        </article>
      </section>

      <footer>
        <p>SML lexical analyzer</p>
        <p>Built for precise language inspection</p>
      </footer>
    </main>
  )
}
