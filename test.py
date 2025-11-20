from giga_start import *
#final


Prompt= "Расскажи о себе" # Сюда впишите ваш запрос
def main():

    answer = response_gigachat(Prompt)
    print(f'Ваш ответ:\n{answer}')

if __name__ == '__main__':
    main()