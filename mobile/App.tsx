import React, { useState } from "react";
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
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";

const API_URL = process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, "");

// Render Free can need extra time to wake the API and yfinance can take several
// seconds on the first market-data request. Keep the client from aborting too early.
const API_TIMEOUT_MS = 60_000;

type Analysis = {
  ticker: string;
  price: number;
  change_percent: number;
  indicators: Record<string, number | null>;
  signal: { label: string; score: number; reasons: string[] };
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

function AppContent() {
  const [ticker, setTicker] = useState("AAPL");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyze() {
    const symbol = ticker.trim().toUpperCase();
    Keyboard.dismiss();
    setError("");

    if (!/^[A-Z0-9.\-]{1,12}$/.test(symbol)) {
      setError("Enter a valid ticker symbol, for example AAPL or MSFT.");
      return;
    }

    if (!API_URL) {
      setError("The market-data service is not configured for this build.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetchWithTimeout(`${API_URL}/analysis/${encodeURIComponent(symbol)}?period=1y`);
      const contentType = response.headers.get("content-type") ?? "";
      const data = contentType.includes("application/json") ? await response.json() : null;

      if (!response.ok) {
        throw new Error(data?.detail ?? `Analysis failed (${response.status}).`);
      }
      if (!data?.ticker || !data?.signal) {
        throw new Error("The market-data service returned an invalid response.");
      }

      setAnalysis(data);
    } catch (e) {
      const errorName = e instanceof Error ? e.name : "";
      const errorMessage = e instanceof Error ? e.message.toLowerCase() : "";

      if (errorName === "AbortError" || errorMessage.includes("canceled") || errorMessage.includes("cancelled")) {
        setError("The market-data service is taking longer than expected. Please try again in a few seconds.");
      } else if (e instanceof TypeError) {
        setError("Could not connect to the market-data service. Check your connection and try again.");
      } else {
        setError(e instanceof Error ? e.message : "Analysis failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.safe} edges={["top", "left", "right"]}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <Text style={styles.eyebrow}>MARKET RESEARCH</Text>
        <Text style={styles.title}>Trading Assistant</Text>
        <Text style={styles.subtitle}>Simple, explainable technical research for public-market tickers.</Text>

        <View style={styles.searchRow}>
          <TextInput
            value={ticker}
            onChangeText={(value) => setTicker(value.toUpperCase())}
            autoCapitalize="characters"
            autoCorrect={false}
            maxLength={12}
            returnKeyType="search"
            onSubmitEditing={analyze}
            style={styles.input}
            placeholder="AAPL"
            placeholderTextColor="#777"
          />
          <Pressable style={({ pressed }) => [styles.button, pressed && styles.buttonPressed]} onPress={analyze} disabled={loading}>
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Analyze</Text>}
          </Pressable>
        </View>

        {error ? <Text style={styles.error}>{error}</Text> : null}

        {analysis ? (
          <View style={styles.card}>
            <View style={styles.row}>
              <View>
                <Text style={styles.ticker}>{analysis.ticker}</Text>
                <Text style={styles.price}>{Number(analysis.price).toFixed(2)}</Text>
              </View>
              <Text style={styles.change}>
                {analysis.change_percent >= 0 ? "+" : ""}{Number(analysis.change_percent).toFixed(2)}%
              </Text>
            </View>

            <View style={styles.signalBox}>
              <Text style={styles.label}>Research signal</Text>
              <Text style={styles.signal}>{analysis.signal.label}</Text>
              <Text style={styles.score}>Score: {analysis.signal.score}</Text>
            </View>

            <Text style={styles.section}>Indicators</Text>
            {[["SMA 20", "sma_20"], ["SMA 50", "sma_50"], ["SMA 200", "sma_200"], ["RSI", "rsi_14"], ["ATR %", "atr_percent"]].map(([label, key]) => (
              <View style={styles.metric} key={key}>
                <Text style={styles.metricLabel}>{label}</Text>
                <Text style={styles.metricValue}>
                  {analysis.indicators[key] == null ? "—" : Number(analysis.indicators[key]).toFixed(2)}
                </Text>
              </View>
            ))}

            <Text style={styles.section}>Why this signal?</Text>
            {analysis.signal.reasons.slice(0, 4).map((reason, index) => (
              <Text key={`${reason}-${index}`} style={styles.reason}>• {reason}</Text>
            ))}
          </View>
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>Start with a ticker</Text>
            <Text style={styles.hint}>Enter a symbol to view price, indicators and an explainable research signal.</Text>
          </View>
        )}

        <View style={styles.disclaimerBox}>
          <Text style={styles.disclaimerTitle}>Educational research only</Text>
          <Text style={styles.disclaimer}>Trading Assistant does not execute trades and does not provide investment, financial, or trading advice. Market data may be delayed or incomplete.</Text>
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
  safe: { flex: 1, backgroundColor: "#0b1020" },
  container: { padding: 20, gap: 14 },
  eyebrow: { color: "#60a5fa", fontSize: 11, fontWeight: "800", letterSpacing: 1.4, marginTop: 4 },
  title: { color: "#fff", fontSize: 30, fontWeight: "700" },
  subtitle: { color: "#9ca3af", fontSize: 15, lineHeight: 21 },
  searchRow: { flexDirection: "row", gap: 10, marginTop: 8 },
  input: { flex: 1, backgroundColor: "#151c30", color: "#fff", borderRadius: 12, paddingHorizontal: 14, height: 48, borderWidth: 1, borderColor: "#29334d", fontSize: 16, fontWeight: "600" },
  button: { backgroundColor: "#2563eb", borderRadius: 12, paddingHorizontal: 18, justifyContent: "center", minWidth: 92 },
  buttonPressed: { opacity: 0.78 },
  buttonText: { color: "#fff", fontWeight: "700", textAlign: "center" },
  card: { backgroundColor: "#151c30", borderRadius: 18, padding: 18, marginTop: 8, borderWidth: 1, borderColor: "#202840" },
  row: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  ticker: { color: "#9ca3af", fontSize: 15 },
  price: { color: "#fff", fontSize: 34, fontWeight: "700", marginTop: 2 },
  change: { color: "#fff", fontSize: 18, fontWeight: "600" },
  signalBox: { borderWidth: 1, borderColor: "#29334d", borderRadius: 14, padding: 14, marginTop: 18 },
  label: { color: "#9ca3af", fontSize: 12 },
  signal: { color: "#fff", fontSize: 22, fontWeight: "700", marginTop: 2 },
  score: { color: "#cbd5e1", marginTop: 4 },
  section: { color: "#fff", fontSize: 17, fontWeight: "700", marginTop: 18, marginBottom: 8 },
  metric: { flexDirection: "row", justifyContent: "space-between", paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: "#202840" },
  metricLabel: { color: "#aab2c0" },
  metricValue: { color: "#fff", fontWeight: "600" },
  reason: { color: "#cbd5e1", lineHeight: 21, marginBottom: 6 },
  emptyState: { backgroundColor: "#11182a", borderRadius: 16, padding: 18, marginTop: 8 },
  emptyTitle: { color: "#fff", fontSize: 17, fontWeight: "700", marginBottom: 4 },
  hint: { color: "#9ca3af", lineHeight: 22 },
  error: { color: "#fca5a5", backgroundColor: "#24151b", borderRadius: 10, padding: 10, marginTop: 6, lineHeight: 19 },
  disclaimerBox: { borderTopWidth: 1, borderTopColor: "#202840", paddingTop: 14, marginTop: 8, marginBottom: 20 },
  disclaimerTitle: { color: "#aab2c0", fontSize: 12, fontWeight: "700", textAlign: "center", marginBottom: 4 },
  disclaimer: { color: "#6b7280", fontSize: 11, lineHeight: 17, textAlign: "center" },
});
