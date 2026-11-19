from datasets import load_dataset
from transformers import (
    GPT2Config,
    GPT2LMHeadModel,
    GPT2TokenizerFast,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments
)

print("Loading Dataset")
raw_dataset = load_dataset("HuggingFaceTB/cosmopedia", "khanacademy", split="train")

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token

config = GPT2Config(
    vocab_size=len(tokenizer),
    n_positions=256,
    n_embd=128,
    n_layer=4,
    n_head=4,
    n_inner=512,
    bos_token_id=tokenizer.bos_token_id,
    eos_token_id=tokenizer.eos_token_id
)
model = GPT2LMHeadModel(config)

def tokenize_function(example):
    return tokenizer(example["text"], truncation=True, max_length=128, padding="max_length")

MODEL_DIR = "./llm_decoder_model"
small_dataset = raw_dataset.select(range(24000))
tokenized_dataset = small_dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=["text"]
)

training_args = TrainingArguments(
    output_dir=MODEL_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=8,
    save_steps=500,
    logging_steps=50,
    learning_rate=5e-4
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
)

trainer.train()

model.save_pretrained(MODEL_DIR)
tokenizer.save_pretrained(MODEL_DIR)