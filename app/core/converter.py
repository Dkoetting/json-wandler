import time
from pathlib import Path

from app.core.models import GPTData, MigrationResult
from app.core.targets import TARGETS, ALL_TARGET_NAMES


def convert_gpt(
    gpt: GPTData,
    targets: list[str],
    mode: str,
    output_dir: Path,
    provider: str = "anthropic",
    api_key: str | None = None,
) -> list[MigrationResult]:
    if "all" in targets:
        targets = ALL_TARGET_NAMES

    results = []
    for target_name in targets:
        start = time.time()

        if target_name not in TARGETS:
            results.append(MigrationResult(
                source_name=gpt.name,
                target=target_name,
                mode=mode,
                status="error",
                error_message=f"Unknown target: {target_name}",
            ))
            continue

        try:
            convert_fn = TARGETS[target_name]

            optimized_content = None
            opt_result = None
            if mode == "optimized" and gpt.has_content:
                from app.core.optimizer import optimize_for_target
                opt_result = optimize_for_target(gpt, target_name, provider=provider, api_key=api_key)
                if opt_result.output:
                    optimized_content = opt_result.output

            output_path = convert_fn(gpt, output_dir, optimized_content=optimized_content)
            duration = int((time.time() - start) * 1000)

            results.append(MigrationResult(
                source_name=gpt.name,
                target=target_name,
                mode=mode,
                status="success",
                output_path=str(output_path),
                duration_ms=duration,
                tokens_input=opt_result.tokens_input if opt_result else 0,
                tokens_output=opt_result.tokens_output if opt_result else 0,
            ))
        except Exception as e:
            results.append(MigrationResult(
                source_name=gpt.name,
                target=target_name,
                mode=mode,
                status="error",
                error_message=str(e),
            ))

    return results
