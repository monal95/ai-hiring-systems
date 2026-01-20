import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import '../styles/CodingChallenge.css';

const formatIO = (value) => {
  if (value === undefined || value === null) return 'Not provided';
  if (typeof value === 'string') return value || 'Not provided';
  try {
    return JSON.stringify(value, null, 2);
  } catch (e) {
    return String(value);
  }
};

const CodingChallenge = ({ token, question, onSubmit, onSkip, initialCode = '' }) => {
  const [code, setCode] = useState(initialCode);
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [testResults, setTestResults] = useState(null);
  const [compileOutput, setCompileOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(localStorage.getItem('codeEditorTheme') === 'dark');
  const [expandedHint, setExpandedHint] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const programmingLanguages = ['Python', 'JavaScript', 'Java', 'C++', 'Go', 'Rust'];

  // Save theme preference
  useEffect(() => {
    localStorage.setItem('codeEditorTheme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  const runTests = async () => {
    if (!code.trim()) {
      setCompileOutput('❌ Please write some code first!');
      return;
    }

    try {
      setLoading(true);
      setCompileOutput('Running tests...');

      const response = await axios.post(
        `${API_BASE_URL}/api/interview/${token}/evaluate-code-strict`,
        {
          code: code,
          language: selectedLanguage.toLowerCase(),
          test_cases: question?.test_cases || []
        }
      );

      const evaluation = response.data.evaluation;
      const results = evaluation.test_results || [];

      setTestResults(results);

      const executionErrors = results.filter(r => r.error);
      if (executionErrors.length) {
        const messages = executionErrors.map(r => r.error).join(' | ');
        setCompileOutput(`⚠️ Test execution error: ${messages}. Check API key/quota and retry.`);
        return;
      }

      // Calculate stats
      const passedCount = results.filter(r => r.passed).length;
      const totalCount = results.length;
      const passPercentage = totalCount > 0 ? (passedCount / totalCount) * 100 : 0;

      if (passedCount === totalCount) {
        setCompileOutput(`✅ All ${totalCount} tests passed!\n\nExecution Time: ${evaluation.execution_time || 'N/A'} ms\nMemory: ${evaluation.memory_usage || 'N/A'} MB`);
      } else {
        setCompileOutput(`⚠️ ${passedCount}/${totalCount} tests passed (${passPercentage.toFixed(0)}%)\n\nFeedback: ${evaluation.feedback || 'Check your logic'}`);
      }
    } catch (error) {
      console.error('Error running tests:', error);
      setCompileOutput('❌ Error evaluating code. Please check your syntax.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!code.trim()) {
      alert('Please write some code before submitting!');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(
        `${API_BASE_URL}/api/interview/${token}/evaluate-code-strict`,
        {
          code: code,
          language: selectedLanguage.toLowerCase(),
          test_cases: question?.test_cases || []
        }
      );

      const evaluation = response.data.evaluation;
      setSubmitted(true);

      // Call parent callback
      if (onSubmit) {
        onSubmit({
          code,
          language: selectedLanguage,
          evaluation
        });
      }
    } catch (error) {
      console.error('Error submitting code:', error);
      alert('Error submitting code');
    } finally {
      setLoading(false);
    }
  };

  if (!question) {
    return <div className={`coding-shell ${darkMode ? 'dark' : 'light'}`}>No question available</div>;
  }

  return (
    <div className={`coding-shell ${darkMode ? 'dark' : 'light'}`}>
      <header className="cc-header" style={{paddingTop: '16px'}}>
        <div className="cc-header-left">
          <div className="cc-eyebrow">{question.difficulty || 'MEDIUM'} • Coding Challenge</div>
          <h1 className="cc-title">{question.title || 'Coding Challenge'}</h1>
          <p className="cc-subtext">{question.description || 'Solve the problem below.'}</p>
        </div>
        <div className="cc-header-right">
          <div className="cc-select">
            <label>Language</label>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              disabled={submitted}
            >
              {programmingLanguages.map((lang) => (
                <option key={lang} value={lang.toLowerCase()}>{lang}</option>
              ))}
            </select>
          </div>
          <button
            className="cc-theme-toggle"
            onClick={() => setDarkMode(!darkMode)}
            aria-label="Toggle theme"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      <div className="cc-body">
        <div className="cc-left">
          <section className="cc-card">
            <div className="cc-card-header">📖 Description</div>
            <p className="cc-text">{question.description || 'No description provided.'}</p>
          </section>

          <section className="cc-card">
            <div className="cc-card-header">📝 Examples</div>
            {question.examples?.length ? (
              <div className="cc-list">
                {question.examples.map((ex, idx) => (
                  <div key={idx} className="cc-io-block">
                    <div className="cc-io-title">Example {idx + 1}</div>
                    <div className="cc-io-pair">
                      <span>Input</span>
                      <pre>{formatIO(ex.input)}</pre>
                    </div>
                    <div className="cc-io-pair">
                      <span>Output</span>
                      <pre>{formatIO(ex.output)}</pre>
                    </div>
                    {ex.explanation && (
                      <div className="cc-io-explain">{ex.explanation}</div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="cc-empty">No examples provided.</div>
            )}
          </section>

          <section className="cc-card">
            <div className="cc-card-header">🧪 Test Cases</div>
            {question.test_cases?.length ? (
              <div className="cc-list">
                {question.test_cases.map((tc, idx) => (
                  <div key={idx} className="cc-io-block">
                    <div className="cc-io-title">Test Case {idx + 1}</div>
                    <div className="cc-io-pair">
                      <span>Input</span>
                      <pre>{formatIO(tc.input)}</pre>
                    </div>
                    <div className="cc-io-pair">
                      <span>Expected</span>
                      <pre>{formatIO(tc.expected_output || tc.output)}</pre>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="cc-empty">No test cases provided.</div>
            )}
          </section>

          <section className="cc-card grid-two">
            <div>
              <div className="cc-card-header">⚙️ Constraints</div>
              {question.constraints?.length ? (
                <ul className="cc-bullets">
                  {question.constraints.map((c, idx) => (
                    <li key={idx}>{c}</li>
                  ))}
                </ul>
              ) : (
                <div className="cc-empty">No constraints provided.</div>
              )}
            </div>
            <div>
              <div className="cc-card-header">💡 Hints</div>
              {question.hints?.length ? (
                <div className="cc-hints">
                  {question.hints.map((hint, idx) => (
                    <details
                      key={idx}
                      open={expandedHint === idx}
                      onClick={() => setExpandedHint(expandedHint === idx ? null : idx)}
                    >
                      <summary>Hint {idx + 1}</summary>
                      <p>{hint}</p>
                    </details>
                  ))}
                </div>
              ) : (
                <div className="cc-empty">No hints available.</div>
              )}
            </div>
          </section>
        </div>

        <div className="cc-right">
          <section className="cc-card">
            <div className="cc-editor-toolbar">
              <div>
                <div className="cc-eyebrow">Editor</div>
                <div className="cc-meta">{code.length} characters</div>
              </div>
              <div className="cc-actions">
                <button
                  className="cc-btn secondary"
                  onClick={runTests}
                  disabled={loading || submitted || !code.trim()}
                >
                  {loading ? 'Running…' : 'Run Tests'}
                </button>
                <button
                  className="cc-btn primary"
                  onClick={handleSubmit}
                  disabled={loading || submitted}
                >
                  {submitted ? 'Submitted' : 'Submit'}
                </button>
                {onSkip && (
                  <button className="cc-btn ghost" onClick={onSkip} disabled={submitted}>
                    Skip
                  </button>
                )}
              </div>
            </div>

            <textarea
              className="cc-editor"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder={`// Write your ${selectedLanguage} solution here...\nfunction solve(input) {\n  // ...\n}`}
              disabled={submitted}
              spellCheck="false"
            />

            {compileOutput && (
              <div className="cc-console">
                <div className="cc-console-label">Output</div>
                <pre>{compileOutput}</pre>
              </div>
            )}

            {testResults?.length ? (
              <div className="cc-test-results">
                <div className="cc-test-header">
                  <span>Test Results</span>
                  <span className="cc-badge">{testResults.filter(r => r.passed).length}/{testResults.length} passed</span>
                </div>
                <div className="cc-test-grid">
                  {testResults.map((r, idx) => (
                    <div key={idx} className={`cc-test ${r.error ? 'fail' : (r.passed ? 'pass' : 'fail')}`}>
                      <div className="cc-test-top">
                        <span>{r.error ? '⚠️' : (r.passed ? '✅' : '❌')} Test {idx + 1}</span>
                        {!r.passed && !r.error && (
                          <span className="cc-chip">Check logic</span>
                        )}
                      </div>
                      {r.error ? (
                        <div className="cc-test-body">
                          <div><strong>Error:</strong> {r.error}</div>
                          {r.compile_output && <div><strong>Compiler:</strong> {r.compile_output}</div>}
                          {r.stderr && <div><strong>Stderr:</strong> {r.stderr}</div>}
                        </div>
                      ) : (!r.passed && (
                        <div className="cc-test-body">
                          <div><strong>Expected:</strong> {formatIO(r.expected)}</div>
                          <div><strong>Got:</strong> {formatIO(r.actual)}</div>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
            ) : null}

            {!compileOutput && !testResults && !submitted && (
              <div className="cc-empty padded">Run tests to see feedback.</div>
            )}

            {submitted && !testResults && (
              <div className="cc-success">Submitted successfully.</div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
};

export default CodingChallenge;
