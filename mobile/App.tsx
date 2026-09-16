import React, { useState } from "react";
import { ActivityIndicator, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import { StatusBar } from "expo-status-bar";

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

type Analysis = {
  ticker: string;
  price: number;
  change_percent: number;
  indicators: Record<string, number | null>;
  signal: { label: string; score: number; reasons: string[] };
  position_size?: number | null;
};

export default function App() {
  const [ticker, setTicker] = useState("AAPL");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyze() {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}/analysis/${ticker.trim().toUpperCase()}?period=1y`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Analysis failed");
      setAnalysis(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Trading Assistant</Text>
        <Text style={styles.subtitle}>Simple market research</Text>

        <View style={styles.searchRow}>
          <TextInput value={ticker} onChangeText={setTicker} autoCapitalize="characters" style={styles.input} placeholder="AAPL" placeholderTextColor="#777" />
          <Pressable style={styles.button} onPress={analyze} disabled={loading}>
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Analyze</Text>}
          </Pressable>
        </View>

        {error ? <Text style={styles.error}>{error}</Text> : null}

        {analysis ? (
          <View style={styles.card}>
            <View style={styles.row}>
              <View>
                <Text style={styles.ticker}>{analysis.ticker}</Text>
                <Text style={styles.price}>{analysis.price.toFixed(2)}</Text>
              </View>
              <Text style={styles.change}>{analysis.change_percent >= 0 ? "+" : ""}{analysis.change_percent.toFixed(2)}%</Text>
            </View>

            <View style={styles.signalBox}>
              <Text style={styles.label}>Signal</Text>
              <Text style={styles.signal}>{analysis.signal.label}</Text>
              <Text style={styles.score}>Score: {analysis.signal.score}</Text>
            </View>

            <Text style={styles.section}>Indicators</Text>
            {[["SMA 20", "sma_20"], ["SMA 50", "sma_50"], ["SMA 200", "sma_200"], ["RSI", "rsi_14"], ["ATR %", "atr_percent"]].map(([label, key]) => (
              <View style={styles.metric} key={key}>
                <Text style={styles.metricLabel}>{label}</Text>
                <Text style={styles.metricValue}>{analysis.indicators[key] == null ? "—" : Number(analysis.indicators[key]).toFixed(2)}</Text>
              </View>
            ))}

            <Text style={styles.section}>Why</Text>
            {analysis.signal.reasons.slice(0, 4).map((reason) => <Text key={reason} style={styles.reason}>• {reason}</Text>)}
          </View>
        ) : (
          <Text style={styles.hint}>Enter a ticker to view price, indicators and an explainable signal.</Text>
        )}

        <Text style={styles.disclaimer}>Educational research only. Not investment advice.</Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#0b1020" },
  container: { padding: 20, gap: 14 },
  title: { color: "#fff", fontSize: 30, fontWeight: "700" },
  subtitle: { color: "#9ca3af", fontSize: 15 },
  searchRow: { flexDirection: "row", gap: 10, marginTop: 8 },
  input: { flex: 1, backgroundColor: "#151c30", color: "#fff", borderRadius: 12, paddingHorizontal: 14, height: 48 },
  button: { backgroundColor: "#2563eb", borderRadius: 12, paddingHorizontal: 18, justifyContent: "center", minWidth: 92 },
  buttonText: { color: "#fff", fontWeight: "700", textAlign: "center" },
  card: { backgroundColor: "#151c30", borderRadius: 18, padding: 18, marginTop: 8 },
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
  hint: { color: "#9ca3af", lineHeight: 22, marginTop: 24 },
  error: { color: "#fca5a5", marginTop: 6 },
  disclaimer: { color: "#6b7280", fontSize: 12, textAlign: "center", marginTop: 18, marginBottom: 20 }
});
