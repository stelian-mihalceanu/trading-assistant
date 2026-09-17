import React, { useMemo, useState } from "react";
import {
  ActivityIndicator,
  Keyboard,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import {
  SafeAreaProvider,
  SafeAreaView,
} from "react-native-safe-area-context";

const API_URL = process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, "");
const API_TIMEOUT_MS = 60_000;

const QUICK_TICKERS = ["AAPL", "MSFT", "NVDA", "TSLA"];

const INDICATORS = [
  ["SMA 20", "sma_20"],
  ["SMA 50", "sma_50"],
  ["SMA 200", "sma_200"],
  ["RSI", "rsi_14"],
  ["ATR %", "atr_percent"],
] as const;

type Analysis = {
  ticker: string;
  price: number;
  change_percent: number;
  indicators: Record<string, number | null>;
  signal: {
    label: string;
    score: number;
    reasons: string[];
  };
  position_size?: number | null;
};

async function fetchWithTimeout(url: string) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT_MS);

  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(timeout);
  }
}

function formatNumber(value: number, digits = 2) {
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
}

function getSignalTone(label: string) {
  const value = label.toLowerCase();

  if (
    value.includes("positive") ||
    value.includes("bull") ||
    value.includes("buy")
  ) {
    return {
      backgroundColor: "#12362c",
      borderColor: "#1f6b55",
      textColor: "#66e0b0",
    };
  }

  if (
    value.includes("negative") ||
    value.includes("bear") ||
    value.includes("sell")
  ) {
    return {
      backgroundColor: "#3a1c24",
      borderColor: "#7b3444",
      textColor: "#ff9cab",
    };
  }

  return {
    backgroundColor: "#2c2a20",
    borderColor: "#61582b",
    textColor: "#f5da72",
  };
}

function AppContent() {
  const [ticker, setTicker] = useState("AAPL");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [recent, setRecent] = useState<string[]>([]);

  const signalTone = useMemo(
    () => (analysis ? getSignalTone(analysis.signal.label) : null),
    [analysis]
  );

  async function analyze(nextTicker = ticker) {
    const symbol = nextTicker.trim().toUpperCase();
    Keyboard.dismiss();
    setError("");

    if (!/^[A-Z0-9.\-]{1,12}$/.test(symbol)) {
      setError("Enter a valid ticker, for example AAPL or MSFT.");
      return;
    }

    if (!API_URL) {
      setError("Market data is not configured for this build.");
      return;
    }

    setTicker(symbol);
    setLoading(true);

    try {
      const response = await fetchWithTimeout(
        `${API_URL}/analysis/${encodeURIComponent(symbol)}?period=1y`
      );
      const contentType = response.headers.get("content-type") ?? "";
      const data = contentType.includes("application/json")
        ? await response.json()
        : null;

      if (!response.ok) {
        throw new Error(data?.detail ?? `Analysis failed (${response.status}).`);
      }

      if (!data?.ticker || !data?.signal) {
        throw new Error("The market-data service returned an invalid response.");
      }

      setAnalysis(data);
      setRecent((current) => [
        symbol,
        ...current.filter((item) => item !== symbol),
      ].slice(0, 5));
    } catch (e) {
      const errorName = e instanceof Error ? e.name : "";
      const errorMessage = e instanceof Error ? e.message.toLowerCase() : "";

      if (
        errorName === "AbortError" ||
        errorMessage.includes("canceled") ||
        errorMessage.includes("cancelled")
      ) {
        setError("The market-data service is taking longer than expected. Try again shortly.");
      } else if (e instanceof TypeError) {
        setError("Could not connect to the market-data service. Check your connection and try again.");
      } else {
        setError(e instanceof Error ? e.message : "Analysis failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  const changePositive = (analysis?.change_percent ?? 0) >= 0;

  return (
    <SafeAreaView style={styles.safe} edges={["top", "bottom"]}>
      <StatusBar style="light" />
      <ScrollView
        contentContainerStyle={styles.container}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.header}>
          <View style={styles.brandMark}>
            <View style={styles.brandBarSmall} />
            <View style={styles.brandBarMedium} />
            <View style={styles.brandBarLarge} />
          </View>
          <View style={styles.brandTextWrap}>
            <Text style={styles.eyebrow}>MARKET INTELLIGENCE</Text>
            <Text style={styles.brand}>Trading Assistant</Text>
          </View>
        </View>

        <View style={styles.heroBlock}>
          <Text style={styles.heroTitle}>Read the market clearly.</Text>
          <Text style={styles.heroSubtitle}>
            Search a ticker and get a focused view of price, trend, momentum,
            volatility, and the reasoning behind the signal.
          </Text>
        </View>

        <View style={styles.searchCard}>
          <Text style={styles.fieldLabel}>Ticker symbol</Text>
          <View style={styles.searchRow}>
            <TextInput
              value={ticker}
              onChangeText={(value) => setTicker(value.toUpperCase())}
              autoCapitalize="characters"
              autoCorrect={false}
              maxLength={12}
              returnKeyType="search"
              onSubmitEditing={() => void analyze()}
              style={styles.input}
              placeholder="AAPL"
              placeholderTextColor="#667085"
              accessibilityLabel="Ticker symbol"
            />
            <Pressable
              style={({ pressed }) => [
                styles.primaryButton,
                pressed && styles.primaryButtonPressed,
              ]}
              onPress={() => void analyze()}
              disabled={loading}
              accessibilityRole="button"
              accessibilityLabel="Analyze ticker"
            >
              {loading ? (
                <ActivityIndicator color="#ffffff" />
              ) : (
                <Text style={styles.primaryButtonText}>Analyze</Text>
              )}
            </Pressable>
          </View>

          <Text style={styles.quickLabel}>Quick symbols</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.quickRow}
          >
            {QUICK_TICKERS.map((symbol) => (
              <Pressable
                key={symbol}
                onPress={() => void analyze(symbol)}
                style={({ pressed }) => [
                  styles.quickChip,
                  pressed && styles.quickChipPressed,
                ]}
              >
                <Text style={styles.quickChipText}>{symbol}</Text>
              </Pressable>
            ))}
            {recent
              .filter((symbol) => !QUICK_TICKERS.includes(symbol))
              .map((symbol) => (
                <Pressable
                  key={`recent-${symbol}`}
                  onPress={() => void analyze(symbol)}
                  style={({ pressed }) => [
                    styles.quickChip,
                    pressed && styles.quickChipPressed,
                  ]}
                >
                  <Text style={styles.quickChipText}>{symbol}</Text>
                </Pressable>
              ))}
          </ScrollView>
        </View>

        {error ? (
          <View style={styles.errorCard}>
            <Text style={styles.errorTitle}>We couldn't complete that search</Text>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        ) : null}

        {analysis ? (
          <>
            <View style={styles.quoteCard}>
              <View>
                <Text style={styles.cardEyebrow}>LATEST QUOTE</Text>
                <Text style={styles.tickerText}>{analysis.ticker}</Text>
                <Text style={styles.priceText}>
                  ${formatNumber(Number(analysis.price))}
                </Text>
                <Text
                  style={[
                    styles.changeText,
                    { color: changePositive ? "#63dfab" : "#ff8e9e" },
                  ]}
                >
                  {changePositive ? "+" : ""}
                  {formatNumber(Number(analysis.change_percent))}% today
                </Text>
              </View>
              {signalTone ? (
                <View
                  style={[
                    styles.signalPill,
                    {
                      backgroundColor: signalTone.backgroundColor,
                      borderColor: signalTone.borderColor,
                    },
                  ]}
                >
                  <Text style={styles.signalPillLabel}>RESEARCH SIGNAL</Text>
                  <Text
                    style={[
                      styles.signalPillText,
                      { color: signalTone.textColor },
                    ]}
                  >
                    {analysis.signal.label}
                  </Text>
                </View>
              ) : null}
            </View>

            <View style={styles.sectionHeader}>
              <View>
                <Text style={styles.sectionTitle}>Technical snapshot</Text>
                <Text style={styles.sectionSubtitle}>
                  Key indicators from the current analysis window.
                </Text>
              </View>
            </View>

            <View style={styles.metricGrid}>
              {INDICATORS.map(([label, key]) => {
                const value = analysis.indicators[key];
                return (
                  <View style={styles.metricCard} key={key}>
                    <Text style={styles.metricLabel}>{label}</Text>
                    <Text style={styles.metricValue}>
                      {value == null ? "—" : formatNumber(Number(value))}
                    </Text>
                  </View>
                );
              })}
            </View>

            <View style={styles.reasonsCard}>
              <Text style={styles.sectionTitle}>Why this signal?</Text>
              <Text style={styles.sectionSubtitle}>
                The signal is built from the indicators above so the output stays interpretable.
              </Text>

              <View style={styles.reasonList}>
                {analysis.signal.reasons.slice(0, 5).map((reason, index) => (
                  <View style={styles.reasonRow} key={`${reason}-${index}`}>
                    <View style={styles.reasonDot} />
                    <Text style={styles.reasonText}>{reason}</Text>
                  </View>
                ))}
              </View>

              <View style={styles.scoreRow}>
                <Text style={styles.scoreLabel}>Signal score</Text>
                <Text style={styles.scoreValue}>{analysis.signal.score}</Text>
              </View>
            </View>

            {analysis.position_size != null ? (
              <View style={styles.positionCard}>
                <View>
                  <Text style={styles.cardEyebrow}>REFERENCE ONLY</Text>
                  <Text style={styles.positionTitle}>Position-size reference</Text>
                  <Text style={styles.positionSubtitle}>
                    Optional sizing output returned by the API.
                  </Text>
                </View>
                <Text style={styles.positionValue}>
                  {formatNumber(Number(analysis.position_size), 0)}
                </Text>
              </View>
            ) : null}
          </>
        ) : (
          <View style={styles.emptyCard}>
            <View style={styles.emptyIcon}>
              <View style={styles.emptyLine} />
              <View style={[styles.emptyLine, styles.emptyLineMiddle]} />
              <View style={[styles.emptyLine, styles.emptyLineTop]} />
            </View>
            <Text style={styles.emptyTitle}>Start with a symbol</Text>
            <Text style={styles.emptyText}>
              Your first search will populate the market snapshot, technical metrics, and explainable signal.
            </Text>
          </View>
        )}

        <View style={styles.disclaimerCard}>
          <Text style={styles.disclaimerTitle}>Educational research only</Text>
          <Text style={styles.disclaimerText}>
            Trading Assistant does not execute trades and does not provide investment, financial, or trading advice. Market data may be delayed or incomplete.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <AppContent />
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: "#070A12",
  },
  container: {
    paddingHorizontal: 18,
    paddingTop: 12,
    paddingBottom: 28,
    gap: 14,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 4,
  },
  brandMark: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: "#0F172A",
    borderWidth: 1,
    borderColor: "#1C2940",
    flexDirection: "row",
    alignItems: "flex-end",
    justifyContent: "center",
    gap: 3,
    paddingBottom: 9,
  },
  brandBarSmall: {
    width: 5,
    height: 10,
    borderRadius: 2.5,
    backgroundColor: "#67E8F9",
  },
  brandBarMedium: {
    width: 5,
    height: 16,
    borderRadius: 2.5,
    backgroundColor: "#60A5FA",
  },
  brandBarLarge: {
    width: 5,
    height: 22,
    borderRadius: 2.5,
    backgroundColor: "#34D399",
  },
  brandTextWrap: {
    marginLeft: 11,
  },
  eyebrow: {
    color: "#64748B",
    fontSize: 9,
    fontWeight: "800",
    letterSpacing: 1.4,
  },
  brand: {
    color: "#F8FAFC",
    fontSize: 17,
    fontWeight: "700",
    marginTop: 1,
  },
  heroBlock: {
    paddingTop: 12,
    paddingBottom: 2,
  },
  heroTitle: {
    color: "#F8FAFC",
    fontSize: 33,
    lineHeight: 39,
    fontWeight: "800",
    letterSpacing: -0.8,
  },
  heroSubtitle: {
    color: "#94A3B8",
    fontSize: 14,
    lineHeight: 21,
    marginTop: 9,
    maxWidth: 370,
  },
  searchCard: {
    backgroundColor: "#0D1422",
    borderWidth: 1,
    borderColor: "#1B273B",
    borderRadius: 20,
    padding: 14,
    marginTop: 2,
  },
  fieldLabel: {
    color: "#CBD5E1",
    fontSize: 12,
    fontWeight: "700",
    marginBottom: 8,
  },
  searchRow: {
    flexDirection: "row",
    gap: 9,
  },
  input: {
    flex: 1,
    height: 48,
    backgroundColor: "#080D17",
    color: "#F8FAFC",
    borderRadius: 14,
    paddingHorizontal: 14,
    borderWidth: 1,
    borderColor: "#22304A",
    fontSize: 16,
    fontWeight: "700",
  },
  primaryButton: {
    minWidth: 100,
    height: 48,
    borderRadius: 14,
    backgroundColor: "#2563EB",
    alignItems: "center",
    justifyContent: "center",
  },
  primaryButtonPressed: {
    opacity: 0.78,
  },
  primaryButtonText: {
    color: "#FFFFFF",
    fontSize: 14,
    fontWeight: "800",
  },
  quickLabel: {
    color: "#64748B",
    fontSize: 11,
    fontWeight: "700",
    marginTop: 13,
    marginBottom: 7,
  },
  quickRow: {
    gap: 7,
  },
  quickChip: {
    paddingHorizontal: 13,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: "#141F31",
    borderWidth: 1,
    borderColor: "#22304A",
  },
  quickChipPressed: {
    backgroundColor: "#1B2B44",
  },
  quickChipText: {
    color: "#CBD5E1",
    fontSize: 12,
    fontWeight: "700",
  },
  errorCard: {
    backgroundColor: "#25141B",
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#582431",
    padding: 14,
  },
  errorTitle: {
    color: "#FFD4DA",
    fontSize: 13,
    fontWeight: "800",
  },
  errorText: {
    color: "#E8A5AE",
    fontSize: 12,
    lineHeight: 18,
    marginTop: 4,
  },
  quoteCard: {
    backgroundColor: "#111A2A",
    borderRadius: 22,
    borderWidth: 1,
    borderColor: "#24324A",
    padding: 18,
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12,
  },
  cardEyebrow: {
    color: "#64748B",
    fontSize: 9,
    fontWeight: "800",
    letterSpacing: 1.3,
  },
  tickerText: {
    color: "#A8B4C8",
    fontSize: 14,
    fontWeight: "700",
    marginTop: 7,
  },
  priceText: {
    color: "#FFFFFF",
    fontSize: 33,
    fontWeight: "800",
    letterSpacing: -0.6,
    marginTop: 1,
  },
  changeText: {
    fontSize: 13,
    fontWeight: "800",
    marginTop: 3,
  },
  signalPill: {
    alignSelf: "flex-start",
    minWidth: 108,
    borderRadius: 14,
    borderWidth: 1,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  signalPillLabel: {
    color: "#64748B",
    fontSize: 8,
    fontWeight: "800",
    letterSpacing: 1,
  },
  signalPillText: {
    fontSize: 14,
    fontWeight: "800",
    marginTop: 4,
  },
  sectionHeader: {
    paddingTop: 5,
  },
  sectionTitle: {
    color: "#F8FAFC",
    fontSize: 17,
    fontWeight: "800",
    letterSpacing: -0.2,
  },
  sectionSubtitle: {
    color: "#7C8BA1",
    fontSize: 12,
    lineHeight: 18,
    marginTop: 3,
  },
  metricGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 9,
  },
  metricCard: {
    width: "48%",
    minHeight: 92,
    backgroundColor: "#0D1422",
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#1B273B",
    padding: 14,
    justifyContent: "space-between",
  },
  metricLabel: {
    color: "#7C8BA1",
    fontSize: 11,
    fontWeight: "700",
  },
  metricValue: {
    color: "#F8FAFC",
    fontSize: 21,
    fontWeight: "800",
    letterSpacing: -0.3,
  },
  reasonsCard: {
    backgroundColor: "#0D1422",
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#1B273B",
    padding: 16,
  },
  reasonList: {
    marginTop: 14,
    gap: 12,
  },
  reasonRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 10,
  },
  reasonDot: {
    width: 7,
    height: 7,
    borderRadius: 3.5,
    backgroundColor: "#5EEAD4",
    marginTop: 6,
  },
  reasonText: {
    flex: 1,
    color: "#C7D2E2",
    fontSize: 13,
    lineHeight: 19,
  },
  scoreRow: {
    marginTop: 15,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: "#1B273B",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  scoreLabel: {
    color: "#7C8BA1",
    fontSize: 11,
    fontWeight: "700",
  },
  scoreValue: {
    color: "#F8FAFC",
    fontSize: 14,
    fontWeight: "800",
  },
  positionCard: {
    backgroundColor: "#111A2A",
    borderRadius: 19,
    borderWidth: 1,
    borderColor: "#24324A",
    padding: 16,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 12,
  },
  positionTitle: {
    color: "#F8FAFC",
    fontSize: 15,
    fontWeight: "800",
    marginTop: 5,
  },
  positionSubtitle: {
    color: "#7C8BA1",
    fontSize: 11,
    lineHeight: 16,
    marginTop: 3,
    maxWidth: 230,
  },
  positionValue: {
    color: "#67E8F9",
    fontSize: 27,
    fontWeight: "800",
  },
  emptyCard: {
    backgroundColor: "#0D1422",
    borderRadius: 22,
    borderWidth: 1,
    borderColor: "#1B273B",
    paddingHorizontal: 20,
    paddingVertical: 24,
    alignItems: "center",
  },
  emptyIcon: {
    width: 52,
    height: 52,
    borderRadius: 16,
    backgroundColor: "#111A2A",
    borderWidth: 1,
    borderColor: "#26344C",
    flexDirection: "row",
    alignItems: "flex-end",
    justifyContent: "center",
    gap: 4,
    paddingBottom: 12,
  },
  emptyLine: {
    width: 6,
    height: 11,
    backgroundColor: "#475569",
    borderRadius: 3,
  },
  emptyLineMiddle: {
    height: 18,
    backgroundColor: "#60A5FA",
  },
  emptyLineTop: {
    height: 25,
    backgroundColor: "#34D399",
  },
  emptyTitle: {
    color: "#F8FAFC",
    fontSize: 17,
    fontWeight: "800",
    marginTop: 13,
  },
  emptyText: {
    color: "#7C8BA1",
    fontSize: 12,
    lineHeight: 18,
    textAlign: "center",
    maxWidth: 315,
    marginTop: 5,
  },
  disclaimerCard: {
    paddingTop: 14,
    borderTopWidth: 1,
    borderTopColor: "#172033",
    marginTop: 3,
  },
  disclaimerTitle: {
    color: "#94A3B8",
    fontSize: 11,
    fontWeight: "800",
    textAlign: "center",
  },
  disclaimerText: {
    color: "#5F6B7D",
    fontSize: 10,
    lineHeight: 16,
    textAlign: "center",
    marginTop: 4,
  },
});
