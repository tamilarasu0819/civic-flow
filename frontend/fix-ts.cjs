const fs = require('fs');

function replaceFile(path, search, replace) {
  let content = fs.readFileSync(path, 'utf8');
  content = content.replace(search, replace);
  fs.writeFileSync(path, content);
}

replaceFile('src/App.tsx', "import React from 'react';\n", '');
replaceFile('src/components/streaming/AnalysisProgressTimeline.tsx', "import { StreamStage }", "import type { StreamStage }");
replaceFile('src/components/ticket/ComplaintPreview.tsx', "import { ComplaintPreviewProps }", "import type { ComplaintPreviewProps }");
replaceFile('src/components/ticket/DepartmentCard.tsx', "import { DepartmentCardProps }", "import type { DepartmentCardProps }");
replaceFile('src/components/ticket/ImageUploader.tsx', "import { UploadCloud, Image as ImageIcon }", "import { UploadCloud }");
replaceFile('src/components/ticket/IssueCategoryCard.tsx', "import { IssueCategoryCardProps }", "import type { IssueCategoryCardProps }");
replaceFile('src/components/ticket/SeverityCard.tsx', "import { SeverityCardProps }", "import type { SeverityCardProps }");
replaceFile('src/hooks/useAIStream.ts', "import { SSEPacket, StreamStage, VisionCompletePayload, TicketCompletePayload }", "import type { StreamStage, VisionCompletePayload, TicketCompletePayload }");
replaceFile('src/hooks/useAIStream.ts', "es.onerror = (err)", "es.onerror = (_err)");
replaceFile('src/hooks/useAIStream.ts', "catch(err)", "catch(_err)");
replaceFile('src/store/useStreamStore.ts', "import { StreamStage, StreamStatus }", "import type { StreamStage, StreamStatus }");
replaceFile('src/store/useStreamStore.ts', "logs: [],", "logs: [] as string[],");
replaceFile('src/store/useTicketStore.ts', "import { GeneratedTicket, VisionAnalysisResult }", "import type { GeneratedTicket, VisionAnalysisResult }");
