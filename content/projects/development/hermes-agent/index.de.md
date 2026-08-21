---
title: "Vom n8n-Workflow zum persönlichen Agentensystem"
slug: "hermes-agent"
date: 2026-07-31
description: "Warum ich meinen n8n-Assistenten durch ein selbstgehostetes Agentensystem für Engineering, Ausdauersport und persönliche Wissensarbeit ersetzt habe."
ShowToc: true
TocOpen: true
draft: true
tags:
  - AI
  - Automatisierung
  - Homelab
  - Obsidian
homepage:
  section: engineering
  state: active
  featured: false
project:
  status: active
---

> Entwurf — diese Projektseite ist noch nicht veröffentlicht.

Mein erster persönlicher KI-Assistent war ein n8n-Workflow: Telegram rein, Modell entscheidet, ein paar MCP-Tools erledigen Kalender, Aufgaben oder Notizen. Das war ein gutes erstes Experiment. Hermes und vergleichbare Agentensysteme hatte ich damals noch nicht auf dem Radar; n8n hat mir gezeigt, welche Dinge ich wirklich automatisieren will.

Im Alltag wurde aber genau diese Form zum Limit. Jede neue Aufgabe brauchte eine eigene Konfiguration, kleine Abweichungen vom erwarteten Input machten den Flow fragil, und der Block-Builder war für meinen Anwendungsfall oft umständlicher als ein kleines Stück Code. Meine Fragen passen ohnehin selten in einen festen Ablauf. Mal geht es um einen Fehler im K3s-Cluster, mal um einen Vergleich zweier Fahrrad-Setups, mal um eine Notiz aus dem Obsidian-Vault oder um die Planung der nächsten Trainingswoche. Dafür wollte ich nicht pro Anwendungsfall wieder einen eigenen Flow, Prompt und Satz von Knoten bauen.

Deshalb läuft heute [Hermes Agent](https://hermes-agent.nousresearch.com/docs) als persönliches Agentensystem in meinem Homelab. Nicht als autonomer Butler, der im Hintergrund beliebige Dinge verändert. Eher als technischer und sportlicher Sparringspartner mit Werkzeugen, Grenzen und einem Gedächtnis, das ich selbst kontrolliere.

## Warum nicht einfach bei n8n bleiben?

n8n bleibt ein gutes Werkzeug für deterministische Automatisierungen: Webhooks verarbeiten, Daten zwischen Diensten schieben, Erinnerungen verschicken, regelmäßig einen Job ausführen. Dort ist ein sichtbarer Workflow ein Vorteil.

Die Arbeit mit einem persönlichen Assistenten beginnt jedoch oft vor der Automatisierung. Ich will zunächst verstehen, was überhaupt los ist:

- Welche Hypothese erklärt diesen Fehler am besten?
- Welche Informationen fehlen für eine Infrastrukturentscheidung?
- Ist die Trainingswoche ambitioniert oder einfach zu viel?
- Gibt es zu einem Thema schon eine brauchbare Notiz oder baue ich gerade ein Duplikat?

Ein Agent kann erst recherchieren, Dateien und Logs lesen, Optionen gegeneinander abwägen und dann einen konkreten nächsten Schritt vorschlagen. Falls aus dem Ergebnis ein stabiler, wiederholbarer Ablauf entsteht, kann daraus immer noch eine klassische Automatisierung werden. Das ist für mich die richtige Reihenfolge: erst Denken und Prüfen, dann automatisieren.

## Was Hermes Agent für mich ist

Hermes ist eine lokal gehostete, Chat-first-Oberfläche über zwei Bereiche, die auf den ersten Blick wenig miteinander zu tun haben: Engineering und Ausdauersport. Ich nutze ihn hauptsächlich über Discord, mit getrennten Channels je Thema; Telegram ist ein weiterer Einstiegspunkt. Text, Sprachnachrichten und Bilder landen im selben Arbeitskontext. In beiden Fällen hilft mir kein allgemeines "Du schaffst das", sondern ein System, das Kontext sauber einordnet und bei Unsicherheit nicht rät.

Im technischen Bereich unterstützt der Agent DevOps, Docker, Kubernetes, Homelab-Betrieb, Debugging, Architektur und den Blog selbst: Abhängigkeiten aktualisieren, SEO verbessern, Shortcodes bauen und GitHub-Actions-Workflows schärfen. Für fokussierte Implementierungsarbeit nutze ich Hermes nicht als primäre Coding-Umgebung, sondern Codex über eine OpenCode-Integration in Neovim. Hermes ist das System darum herum: Es recherchiert, strukturiert und hilft dabei, aus einem groben GitOps-Deployment eine brauchbare Basis zu machen. Die gewünschte Arbeitsweise ist bewusst nüchtern: zuerst Zielbild, Risiken und Trade-offs klären; dann Logs und Status ansehen; Hypothesen bilden; gezielt testen; erst danach ändern.

Im Sportbereich arbeitet derselbe Agent mit einem anderen Satz von Fragen: Wie passt die tatsächliche Belastung zur Planung? Wo fehlt Erholung? Was sagt die Entwicklung der letzten Wochen über die Vorbereitung auf ein Event? Welche Ausrüstung löst ein echtes Problem und welche ist nur ein teures Upgrade? Training ist für mich dabei nicht vom Rest des Alltags getrennt. Schlaf, Mobility, Yoga, Krafttraining und verfügbare Zeit gehören in dieselbe Betrachtung.

Der gemeinsame Nenner ist kein magischer Prompt. Es sind klare Rollen, Regeln und Datenquellen.

## Architektur: ein Agent mit klaren Grenzen

Der Betrieb ist Docker-basiert, mit einem Tailscale-Sidecar. Das ist keine Sicherheitsgarantie, aber eine wichtige Grenze zwischen Agent und Host. Wichtige lokale Verzeichnisse, darunter der Obsidian-Vault, sind bewusst als Volumes eingebunden. Keys und Secrets werden als Umgebungsvariablen übergeben und gehören weder in Antworten noch in Git-Repositories. Der Agent bekommt nicht pauschal alles, sondern nur die Zugriffe, die für seine Aufgaben nötig sind.

Diese Trennung ist besonders relevant, weil der Agent nicht nur Texte zusammenfasst. Er kann bei Bedarf Dateien lesen, Logs prüfen, Skripte ausführen oder definierte Dienste abfragen. Genau deshalb braucht jede Fähigkeit einen klaren Rahmen.

Für Infrastrukturarbeit bedeutet das zum Beispiel:

1. Zuerst read-only prüfen: Status, Logs, Konfiguration und Abhängigkeiten.
2. Änderungen so klein und reversibel wie möglich halten.
3. Bei Migrationen, Volumes, Datenbanken, Löschoperationen oder unklaren Folgen vorher anhalten.
4. Dry-runs, Backups und einen möglichen Rollback prüfen, bevor etwas Produktives verändert wird.

Das klingt konservativ, ist aber der Punkt. Ein Agent, der bei einem falsch verstandenen Satz sofort `prune` oder `delete` ausführt, ist kein hilfreicher Operator.

## Obsidian ist Wissensquelle, nicht Spielwiese

Mein Obsidian-Vault ist das langfristige Gedächtnis des Systems. Dort liegen technische Notizen, Projektkontext, Trainings- und Gesundheitslogs, Rechercheergebnisse und persönliche Routinen. Er ist als Volume eingebunden und wird mit Syncthing auf andere Geräte synchronisiert. Der Agent darf daraus lesen und bestehende passende Notizen ergänzen, aber er soll den Vault nicht "optimieren", indem er Dateien umbenennt, verschiebt oder eine neue Ordnerstruktur erfindet.

Die Schreibregel ist deshalb einfach:

- Zuerst nach einer passenden bestehenden Notiz suchen.
- Wenn sie existiert, gezielt ergänzen statt eine Parallelnotiz anzulegen.
- Wenn der Zielort unklar ist, nachfragen.
- Aufgaben nicht ungefragt in den Vault kippen.

Das schützt vor einem sehr typischen KI-Problem: viel formal korrekter, aber unbrauchbar verstreuter Output. Ein Vault wird nicht besser, weil darin mehr Markdown liegt. Er wird besser, wenn Informationen an der Stelle landen, an der ich sie später wiederfinde.

## Wie ich ihn tatsächlich nutze

### Engineering und Homelab

Der größte Nutzen entsteht nicht durch das Generieren von Boilerplate. Der Agent hilft vor allem dabei, Fehler und Entscheidungen zu strukturieren. Bei einem Problem im Homelab beginnt er mit der Frage, was beobachtbar ist: Welche Komponente ist betroffen? Was sagen Logs, Netzwerkpfad und aktueller Zustand? Welche Annahme lässt sich mit einem kleinen, ungefährlichen Test widerlegen?

Bei Architekturfragen vergleicht er Optionen nach Wartbarkeit, Komplexität, Sicherheitsfläche, Betrieb und Reversibilität. Das bremst Aktionismus. Nicht jede Aufgabe braucht Kubernetes, Terraform oder noch einen Service. Wenn Docker Compose sauber genug ist, soll die Empfehlung auch so aussehen.

### Training und Gesundheit

Für den Sport nutze ich Trainingshistorie, Plan, Zonen und Belastung als Ausgangspunkt. Intervals.icu ist dabei die Hauptquelle, ergänzt durch Garmin-Daten und begrenzt nutzbare Strava-Daten. Ein sinnvoller Review vergleicht nicht nur eine einzelne Fahrt mit einer Zielzahl, sondern schaut auf mehrere Wochen: Umfang, Intensität, längste Einheiten, Ruhetage, Entwicklung von Fitness und Ermüdung.

Wichtig ist die Lücke zwischen Sensorik und Realität. Herzfrequenzlast sagt nicht alles. Ein Krafttraining kann das System wenig belasten und trotzdem Rücken, Schultern oder Rumpf für die nächste harte Radeinheit müde machen. Deshalb gehören auch subjektives Gefühl, Muskelkater, Schmerz und ungewohnte Belastungen in die Bewertung.

Bei Schmerzen, Warnzeichen oder einer sich verschlechternden Beschwerde bleibt der Agent absichtlich konservativ. Er kann keine Diagnose stellen. Seine Aufgabe ist dann, Belastung zu reduzieren, Warnzeichen klar zu benennen und bei anhaltenden Problemen Arzt oder Physio zu empfehlen.

### Wochenreview statt Themenchaos

Der Agent verbindet die beiden Domänen nicht künstlich, aber er hilft beim Priorisieren. Ein Wochenreview beantwortet wenige Fragen:

- Was lief gut?
- Was ist offen oder blockiert?
- Welche Entscheidung steht an?
- Was sind die nächsten ein bis drei sinnvollen Schritte?

Das ist nützlicher als eine endlose To-do-Liste. Auch im Sport verhindert es, dass jede freie Stunde sofort mit Training gefüllt wird. Fortschritt entsteht durch belastbare Routinen, nicht durch maximale Auslastung.

## Was ich bewusst nicht automatisiere

Der Agent darf Vorschläge machen und kleine, reversible Dinge erledigen. Er soll aber nicht ungefragt wichtige Dateien überschreiben, den Obsidian-Vault umbauen, Infrastruktur umstellen oder Gesundheitsentscheidungen treffen.

Diese Grenze ist nicht bloß eine Sicherheitsmaßnahme. Sie hält Verantwortung dort, wo sie hingehört. Ich entscheide über Ziele, Risiko und Prioritäten. Der Agent hilft mir, die Entscheidung mit besserer Information und weniger Reibung zu treffen.

Auch seine Antworten müssen überprüfbar bleiben. Bei aktuellen Tools, Versionen, Preisen, Produkten, Events oder Gesundheitsthemen recherchiert er zuerst und nennt Quellen. Wenn keine belastbare Quelle vorhanden ist, soll er das sagen statt eine plausible Antwort zu erfinden.

## Der aktuelle Stand

Das System ist kein fertiger "Life OS"-Baukasten. Es ist eine wachsende Arbeitsumgebung, die sich an meinen tatsächlichen Projekten orientiert: Homelab-Betrieb, Softwareentwicklung, Obsidian, Laufen und Radfahren. Die stärksten Alltagsanwendungen sind Trainingsfeedback dokumentieren, einen Trainingsreview erstellen, beim Homelab helfen und die einfache, häufige Frage beantworten: "Was habe ich dazu schon in meinen Notizen?" Manche Integrationen sind schon praktisch, andere brauchen noch bessere Schnittstellen oder mehr zuverlässige Daten.

Der wichtigste Fortschritt ist trotzdem bereits da: Aus einzelnen Chat-Anfragen und separaten n8n-Flows ist ein System geworden, das Kontext über längere Zeit halten kann, Risiken ernst nimmt und bei der Umsetzung nicht nur Tempo, sondern auch Wartbarkeit und Erholung berücksichtigt. Menschliches Urteil bleibt nötig: Architekturentscheidungen treffe ich selbst, Recherchequalität schwankt und Trainingspläne brauchen oft noch eine zweite Überarbeitung. Das ist keine Enttäuschung, sondern eine Grenze, die das System erst nützlich macht.

Das ist für mich die interessante Seite persönlicher Agenten. Nicht ein weiterer Bot, der möglichst viel verspricht, sondern ein Werkzeug, das in einem klaren Rahmen zuverlässig mitarbeitet.
