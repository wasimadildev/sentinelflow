# Runtime-only, minimal and nonroot; pin this base to an audited digest in Phase 2.
FROM gcr.io/distroless/nodejs22-debian13:nonroot
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=8080
COPY --chown=nonroot:nonroot apps/api/src/ ./src/
USER nonroot:nonroot
EXPOSE 8080
CMD ["src/server.mjs"]
